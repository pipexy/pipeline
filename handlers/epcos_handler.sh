# Handler dla EPCOS
#!/bin/bash
# epcos_handler.sh
# Handler dla wirtualnej drukarki EPCOS

# Konfiguracja
OUTPUT_DIR="/tmp/printer-emulation/output"
LOG_FILE="/tmp/printer-emulation/logs/epcos-handler.log"
EMULATOR_API="http://localhost:5000/api/emulate/epcos"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Tworzenie katalogów
mkdir -p "$OUTPUT_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Logowanie
log() {
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> "$LOG_FILE"
  echo "[EPCOS Handler] $1"
}

# Główna funkcja obsługi
handle_print_job() {
  log "Otrzymano zadanie drukowania"

  # Katalog dla tego zadania
  JOB_DIR="$OUTPUT_DIR/epcos_$TIMESTAMP"
  mkdir -p "$JOB_DIR"

  # Zapisanie danych wejściowych
  INPUT_FILE="$JOB_DIR/input.epcos"
  cat > "$INPUT_FILE"

  log "Zadanie zapisane w $INPUT_FILE"

  # Sprawdzenie czy plik został zapisany prawidłowo
  if [ ! -s "$INPUT_FILE" ]; then
    log "Błąd: Plik wejściowy jest pusty"
    exit 1
  fi

  # Wywołanie API emulatora
  if command -v curl &> /dev/null; then
    log "Próba wywołania API emulatora"

    # Wywołanie API emulatora
    curl -s -o "$JOB_DIR/output.png" -F "file=@$INPUT_FILE" -F "emulator=epcos" "$EMULATOR_API?dpi=300"

    if [ -f "$JOB_DIR/output.png" ] && [ -s "$JOB_DIR/output.png" ]; then
      log "Podgląd wydruku zapisany w $JOB_DIR/output.png"
    else
      log "Błąd wywołania API emulatora"
      rm -f "$JOB_DIR/output.png"  # Usuń pusty plik
    fi
  fi

  # Alternatywne użycie CLI emulatora
  if [ ! -f "$JOB_DIR/output.png" ] && command -v python3 &> /dev/null; then
    log "Próba lokalnej emulacji za pomocą CLI"

    if [ -f "./runners/cli.py" ]; then
      python3 ./runners/cli.py run --pipeline "epcos.dpi(300).width(210).height(297).output_path('$JOB_DIR/output.png')" --input "$INPUT_FILE"

      if [ $? -eq 0 ]; then
        log "Lokalna emulacja zakończona sukcesem"
      else
        log "Błąd lokalnej emulacji"
      fi
    else
      log "CLI emulatora nie znalezione"
    fi
  fi

  log "Przetwarzanie zakończone"
  echo "Zadanie wydruku przetworzone. Wyniki w $JOB_DIR"
}

# Wykonanie głównej funkcji
handle_print_job