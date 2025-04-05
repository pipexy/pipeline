# Handler dla PCL
#!/bin/bash
# pcl_handler.sh
# Handler dla wirtualnej drukarki PCL

# Konfiguracja
OUTPUT_DIR="/tmp/printer-emulation/output"
LOG_FILE="/tmp/printer-emulation/logs/pcl-handler.log"
EMULATOR_API="http://localhost:5000/api/emulate/pcl"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Tworzenie katalogów
mkdir -p "$OUTPUT_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Logowanie
log() {
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> "$LOG_FILE"
  echo "[PCL Handler] $1"
}

# Główna funkcja obsługi
handle_print_job() {
  log "Otrzymano zadanie drukowania"

  # Katalog dla tego zadania
  JOB_DIR="$OUTPUT_DIR/pcl_$TIMESTAMP"
  mkdir -p "$JOB_DIR"

  # Zapisanie danych wejściowych
  INPUT_FILE="$JOB_DIR/input.pcl"
  cat > "$INPUT_FILE"

  log "Zadanie zapisane w $INPUT_FILE"

  # Sprawdzenie czy plik został zapisany prawidłowo
  if [ ! -s "$INPUT_FILE" ]; then
    log "Błąd: Plik wejściowy jest pusty"
    exit 1
  fi

  # Próba konwersji za pomocą Ghostscript
  if command -v gs &> /dev/null; then
    log "Konwersja PCL do PDF za pomocą Ghostscript"
    PDF_OUTPUT="$JOB_DIR/output.pdf"
    PNG_OUTPUT="$JOB_DIR/output.png"

    # Konwersja PCL -> PDF
    gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="$PDF_OUTPUT" "$INPUT_FILE"

    if [ -f "$PDF_OUTPUT" ]; then
      log "PCL skonwertowany do PDF: $PDF_OUTPUT"

      # Konwersja PDF -> PNG dla podglądu
      gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r300 -sOutputFile="$PNG_OUTPUT" "$PDF_OUTPUT"

      if [ -f "$PNG_OUTPUT" ]; then
        log "Podgląd wydruku zapisany w $PNG_OUTPUT"
      fi
    else
      log "Błąd konwersji PCL do PDF"
    fi
  else
    log "Ghostscript nie jest zainstalowany, próba wywołania API emulatora"
  fi

  # Wywołanie API emulatora jeśli nie udało się lokalnie wygenerować podglądu
  if [ ! -f "$JOB_DIR/output.png" ] && command -v curl &> /dev/null; then
    log "Próba wywołania API emulatora"

    # Wywołanie API emulatora
    curl -s -o "$JOB_DIR/output.png" -F "file=@$INPUT_FILE" -F "emulator=pcl" "$EMULATOR_API?dpi=300"

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
      python3 ./runners/cli.py run --pipeline "pcl.mode('ghostscript').dpi(300).format('png').output_path('$JOB_DIR/output.png')" --input "$INPUT_FILE"

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