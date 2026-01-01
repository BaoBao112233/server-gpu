#!/bin/bash
# Convenience commands for managing Mini Orca server

case "$1" in
    start)
        echo "Starting Mini Orca server..."
        docker-compose up -d
        echo "✓ Server started"
        echo "View logs: ./mini-orca.sh logs"
        ;;
    
    stop)
        echo "Stopping Mini Orca server..."
        docker-compose down
        echo "✓ Server stopped"
        ;;
    
    restart)
        echo "Restarting Mini Orca server..."
        docker-compose restart
        echo "✓ Server restarted"
        ;;
    
    logs)
        docker-compose logs -f llama-cpp-server
        ;;
    
    status)
        echo "Container status:"
        docker-compose ps
        echo ""
        echo "Resource usage:"
        docker stats mini-orca-server --no-stream
        ;;
    
    test)
        echo "Running API tests..."
        python3 scripts/test_mini_orca.py
        ;;
    
    shell)
        echo "Opening shell in container..."
        docker-compose exec llama-cpp-server /bin/bash
        ;;
    
    rebuild)
        echo "Rebuilding container..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo "✓ Rebuild complete"
        ;;
    
    clean)
        echo "Cleaning up..."
        docker-compose down -v
        docker system prune -f
        echo "✓ Cleanup complete"
        ;;
    
    *)
        echo "Mini Orca Server Management"
        echo ""
        echo "Usage: ./mini-orca.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start      Start the server"
        echo "  stop       Stop the server"
        echo "  restart    Restart the server"
        echo "  logs       View server logs"
        echo "  status     Show container status and resource usage"
        echo "  test       Run API tests"
        echo "  shell      Open shell in container"
        echo "  rebuild    Rebuild and restart container"
        echo "  clean      Stop and clean up containers/volumes"
        echo ""
        ;;
esac
