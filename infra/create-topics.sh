#!/usr/bin/env bash
set -euo pipefail

BROKER="${BROKER:-kafka:9092}"

topics=("expenses.raw" "expenses.parsed" "insights.events")

for t in "${topics[@]}"; do
  echo "Creating topic: $t (if not exists)"
  /opt/bitnami/kafka/bin/kafka-topics.sh --create --if-not-exists \
    --bootstrap-server "$BROKER" --replication-factor 1 --partitions 3 --topic "$t" || true
done

echo "Done."
