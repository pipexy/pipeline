# Skrypt startowy
#!/bin/bash
# docker/entrypoint.sh
set -e

# Aktywacja wirtualnego środowiska jeśli istnieje
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Funkcje pomocnicze
setup_dirs() {
    mkdir -p ${DATA_DIR:-./data}
    mkdir -p ${OUTPUT_DIR:-./output}
    mkdir -p ${MODELS_DIR:-./models}
    mkdir -p ${REPORTS_DIR:-./reports}
    mkdir -p ${LOG_DIR:-./logs}
}

wait_for_service() {
    local host=$1
    local port=$2
    local service=$3

    echo "Waiting for $service at $host:$port..."
    while ! nc -z $host $port; do
        sleep 0.5
    done
    echo "$service is available"
}

# Ustawienie katalogów
setup_dirs

# Główna logika
case "$1" in
    api)
        echo "Starting API server..."
        exec python -m runners.api
        ;;
    cli)
        shift
        echo "Running CLI..."
        exec python -m runners.cli "$@"
        ;;
    workflow)
        shift
        echo "Running workflow CLI..."
        exec python -m runners.workflow_cli "$@"
        ;;
    web)
        echo "Starting web interface..."
        exec python -m runners.web_ui
        ;;
    *)
        echo "Running custom command..."
        exec "$@"
        ;;
esac