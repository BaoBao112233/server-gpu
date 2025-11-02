import json
import time
import uuid
from typing import AsyncGenerator, List, Dict, Any
import httpx
from app.backends.base import BaseBackend
from app.models import ChatCompletionRequest


class OllamaBackend(BaseBackend):
    """Ollama backend implementation"""
    
    def __init__(self, base_url: str, default_model: str):
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def chat_completion(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """Generate a chat completion using Ollama"""
        url = f"{self.base_url}/api/chat"
        
        # Convert messages to Ollama format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        payload = {
            "model": request.model or self.default_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "top_p": request.top_p,
                "num_predict": request.max_tokens,
            }
        }
        
        if request.stop:
            payload["options"]["stop"] = request.stop
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Convert Ollama response to OpenAI format
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model or self.default_model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": data.get("message", {}).get("content", "")
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                }
            }
        except httpx.HTTPError as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion using Ollama"""
        url = f"{self.base_url}/api/chat"
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        payload = {
            "model": request.model or self.default_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": request.temperature,
                "top_p": request.top_p,
                "num_predict": request.max_tokens,
            }
        }
        
        if request.stop:
            payload["options"]["stop"] = request.stop
        
        try:
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # Convert to OpenAI streaming format
                        chunk = {
                            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": request.model or self.default_model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {
                                        "content": data.get("message", {}).get("content", "")
                                    },
                                    "finish_reason": "stop" if data.get("done") else None
                                }
                            ]
                        }
                        
                        yield f"data: {json.dumps(chunk)}\n\n"
                        
                        if data.get("done"):
                            yield "data: [DONE]\n\n"
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except httpx.HTTPError as e:
            raise Exception(f"Ollama streaming error: {str(e)}")
    
    async def get_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        """Generate embeddings using Ollama"""
        url = f"{self.base_url}/api/embeddings"
        
        embeddings = []
        for text in texts:
            payload = {
                "model": model,
                "prompt": text
            }
            
            try:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                embeddings.append(data.get("embedding", []))
            except httpx.HTTPError as e:
                raise Exception(f"Ollama embeddings error: {str(e)}")
        
        return embeddings
    
    async def list_models(self) -> List[str]:
        """List available Ollama models"""
        url = f"{self.base_url}/api/tags"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except httpx.HTTPError as e:
            raise Exception(f"Ollama list models error: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if Ollama is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
