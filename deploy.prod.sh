#!/bin/bash
# Production deployment script
# Usage: ./deploy.prod.sh [up|down|restart|logs]

set -e

COMMAND="${1:-up}"

case "$COMMAND" in
  up)
    echo "Starting production containers (no exposed ports for db/redis)..."
    docker compose -f docker-compose.yml up -d
    echo "✓ Production containers started"
    docker compose -f docker-compose.yml ps
    ;;
  down)
    echo "Stopping production containers..."
    docker compose -f docker-compose.yml down
    echo "✓ Production containers stopped"
    ;;
  restart)
    echo "Restarting production containers..."
    docker compose -f docker-compose.yml restart
    echo "✓ Production containers restarted"
    ;;
  logs)
    echo "Streaming production logs (Ctrl+C to exit)..."
    docker compose -f docker-compose.yml logs -f
    ;;
  *)
    echo "Usage: $0 {up|down|restart|logs}"
    echo ""
    echo "Commands:"
    echo "  up       - Start production containers"
    echo "  down     - Stop production containers"
    echo "  restart  - Restart production containers"
    echo "  logs     - Stream production logs"
    exit 1
    ;;
esac
