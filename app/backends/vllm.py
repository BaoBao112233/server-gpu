import json
import time
import uuid
import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional
from app.backends.base import BaseBackend
from app.models import ChatCompletionRequest


class VLLMBackend(BaseBackend):
    """vLLM backend implementation with memory optimization for 24GB VRAM"""
    
    def __init__(self, 
                 model_name: str,
                 gpu_memory_utilization: float = 0.85,
                 max_model_len: int = 4096,
                 tensor_parallel_size: int = 1,
                 dtype: str = "auto"):
        self.model_name = model_name
        self.gpu_memory_utilization = gpu_memory_utilization
        self.max_model_len = max_model_len
        self.tensor_parallel_size = tensor_parallel_size
        self.dtype = dtype
        self.engine = None
        self.tokenizer = None
        
    async def _initialize(self):
        """Lazy initialization of vLLM engine"""
        if self.engine is not None:
            return
            
        try:
            from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
            from transformers import AutoTokenizer
            
            # Configure engine for optimal 24GB VRAM usage
            engine_args = AsyncEngineArgs(
                model=self.model_name,
                gpu_memory_utilization=self.gpu_memory_utilization,
                max_model_len=self.max_model_len,
                tensor_parallel_size=self.tensor_parallel_size,
                dtype=self.dtype,
                trust_remote_code=True,
                enforce_eager=False,  # Use CUDA graphs for better performance
                max_num_seqs=16,  # Adjust based on available memory
                enable_prefix_caching=True,  # Enable KV cache optimization
            )
            
            self.engine = AsyncLLMEngine.from_engine_args(engine_args)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            
        except Exception as e:
            raise Exception(f"Failed to initialize vLLM engine: {str(e)}")
    
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """Generate a chat completion using vLLM"""
        await self._initialize()
        
        from vllm import SamplingParams
        
        # Convert messages to prompt
        prompt = self._format_chat_messages(request.messages)
        
        # Configure sampling parameters
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens or 2048,
            stop=request.stop if request.stop else None,
        )
        
        try:
            # Generate completion
            request_id = str(uuid.uuid4())
            
            # Add request to engine
            results_generator = self.engine.generate(
                prompt,
                sampling_params,
                request_id
            )
            
            # Wait for completion
            final_output = None
            async for output in results_generator:
                final_output = output
            
            if not final_output:
                raise Exception("No output generated")
            
            generated_text = final_output.outputs[0].text
            
            # Count tokens (approximate)
            prompt_tokens = len(self.tokenizer.encode(prompt))
            completion_tokens = len(self.tokenizer.encode(generated_text))
            
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": self.model_name,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": generated_text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            }
        except Exception as e:
            raise Exception(f"vLLM generation error: {str(e)}")
    
    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion using vLLM"""
        await self._initialize()
        
        from vllm import SamplingParams
        
        prompt = self._format_chat_messages(request.messages)
        
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens or 2048,
            stop=request.stop if request.stop else None,
        )
        
        try:
            request_id = str(uuid.uuid4())
            
            results_generator = self.engine.generate(
                prompt,
                sampling_params,
                request_id
            )
            
            previous_text = ""
            async for output in results_generator:
                current_text = output.outputs[0].text
                new_text = current_text[len(previous_text):]
                
                if new_text:
                    chunk = {
                        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": self.model_name,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "content": new_text
                                },
                                "finish_reason": None
                            }
                        ]
                    }
                    
                    yield f"data: {json.dumps(chunk)}\n\n"
                    previous_text = current_text
            
            # Send final chunk
            final_chunk = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": self.model_name,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }
                ]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            raise Exception(f"vLLM streaming error: {str(e)}")
    
    def _format_chat_messages(self, messages: List[Any]) -> str:
        """Format chat messages into a prompt string"""
        # Try to use tokenizer's chat template if available
        if hasattr(self.tokenizer, 'apply_chat_template'):
            try:
                formatted = self.tokenizer.apply_chat_template(
                    [{"role": msg.role, "content": msg.content} for msg in messages],
                    tokenize=False,
                    add_generation_prompt=True
                )
                return formatted
            except:
                pass
        
        # Fallback to simple concatenation
        prompt = ""
        for msg in messages:
            if msg.role == "system":
                prompt += f"System: {msg.content}\n\n"
            elif msg.role == "user":
                prompt += f"User: {msg.content}\n\n"
            elif msg.role == "assistant":
                prompt += f"Assistant: {msg.content}\n\n"
        
        prompt += "Assistant: "
        return prompt
    
    async def get_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        """vLLM doesn't support embeddings - raise error"""
        raise NotImplementedError("vLLM backend doesn't support embeddings. Use Ollama or dedicated embedding models.")
    
    async def list_models(self) -> List[str]:
        """List available models (just the current model)"""
        return [self.model_name]
    
    async def health_check(self) -> bool:
        """Check if vLLM engine is healthy"""
        try:
            await self._initialize()
            return self.engine is not None
        except:
            return False
    
    async def __aenter__(self):
        await self._initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass
