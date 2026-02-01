#!/bin/bash
cd "$(dirname "$0")"
echo "🛑 Fermo i servizi..."
docker compose down
echo "✅ Servizi fermati"
