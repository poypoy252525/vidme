#!/bin/bash
# Development deployment script
# Usage: ./deploy.dev.sh [up|down|restart|logs]

set -e

COMMAND="${1:-up}"

case "$COMMAND" in
  up)
    echo "Starting development containers (with exposed ports for db/redis)..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    echo "✓ Development containers started"
    docker compose -f docker-compose.yml -f docker-compose.dev.yml ps
    echo ""
    echo "Access points:"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis:      localhost:6379"
    echo "  - Web:        localhost:8300"
    ;;
  down)
    echo "Stopping development containers..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml down
    echo "✓ Development containers stopped"
    ;;
  restart)
    echo "Restarting development containers..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml restart
    echo "✓ Development containers restarted"
    ;;
  logs)
    echo "Streaming development logs (Ctrl+C to exit)..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
    ;;
  *)
    echo "Usage: $0 {up|down|restart|logs}"
    echo ""
    echo "Commands:"
    echo "  up       - Start development containers"
    echo "  down     - Stop development containers"
    echo "  restart  - Restart development containers"
    echo "  logs     - Stream development logs"
    exit 1
    ;;
esac
