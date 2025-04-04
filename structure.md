printer-emulator/
├── adapters/                          # Katalog z adapterami
│   ├── base.py                        # Bazowa klasa adapterów
│   ├── bash_adapter.py                # Adapter dla poleceń bash
│   ├── http_client_adapter.py         # Adapter klienta HTTP
│   ├── http_server_adapter.py         # Adapter serwera HTTP
│   ├── file_adapter.py                # Adapter operacji na plikach
│   ├── python_adapter.py              # Adapter dla kodu Python
│   ├── database_adapter.py            # Adapter do baz danych
│   ├── ml_adapter.py                  # Adapter dla Machine Learning
│   ├── message_queue_adapter.py       # Adapter dla systemów kolejkowych
│   ├── websocket_adapter.py           # Adapter dla WebSocket
│   ├── conditional_adapter.py         # Adapter dla warunków
│   ├── zpl_adapter.py                 # Adapter dla języka ZPL
│   ├── escpos_adapter.py              # Adapter dla języka ESC/POS
│   ├── pcl_adapter.py                 # Adapter dla języka PCL
│   ├── epcos_adapter.py               # Adapter dla języka EPCOS
│   └── __init__.py                    # Plik inicjalizacyjny z rejestracją adapterów
│
├── core/                              # Rdzeń systemu
│   ├── pipeline_engine.py             # Silnik wykonujący sekwencje adapterów
│   ├── dsl_parser.py                  # Parser dla składni DSL
│   ├── workflow_engine.py             # Silnik workflow ze wsparciem zależności
│   ├── adapter_manager.py             # Zarządzanie adapterami
│   ├── context.py                     # Klasa kontekstu wykonania
│   └── __init__.py                    # Inicjalizacja rdzenia
│
├── handlers/                          # Handlery do drukarek
│   ├── zpl_handler.sh                 # Handler dla ZPL
│   ├── escpos_handler.sh              # Handler dla ESC/POS
│   ├── pcl_handler.sh                 # Handler dla PCL
│   └── epcos_handler.sh               # Handler dla EPCOS
│
├── emulators/                         # Implementacje emulatorów drukarek
│   ├── zpl/                           # Emulator ZPL
│   │   ├── parser.py                  # Parser poleceń ZPL
│   │   ├── renderer.py                # Renderer ZPL
│   │   └── __init__.py                # Inicjalizacja
│   ├── escpos/                        # Emulator ESC/POS
│   │   ├── parser.py                  # Parser poleceń ESC/POS
│   │   ├── renderer.py                # Renderer ESC/POS
│   │   └── __init__.py                # Inicjalizacja
│   ├── pcl/                           # Emulator PCL
│   │   ├── parser.py                  # Parser poleceń PCL
│   │   ├── renderer.py                # Renderer PCL
│   │   └── __init__.py                # Inicjalizacja
│   └── __init__.py                    # Inicjalizacja modułu emulatorów
│
├── runners/                           # Narzędzia uruchamiające
│   ├── cli.py                         # Interfejs linii poleceń
│   ├── api.py                         # Serwer API
│   ├── workflow_cli.py                # CLI dla workflow
│   └── docker_runner.py               # Wsparcie dla Dockera
│
├── pipelines/                         # Przykładowe pipeline'y w YAML
│   ├── zpl_emulation.yaml             # Pipeline emulacji ZPL
│   ├── escpos_emulation.yaml          # Pipeline emulacji ESC/POS
│   ├── pcl_emulation.yaml             # Pipeline emulacji PCL
│   └── data_analysis.yaml             # Pipeline analizy danych
│
├── workflows/                         # Definicje workflow w YAML
│   ├── printer_comparison.yaml        # Workflow porównania drukarek
│   ├── etl_pipeline.yaml              # Workflow ETL
│   └── monitoring_workflow.yaml       # Workflow monitoringu
│
├── examples/                          # Przykładowe skrypty i dokumentacja
│   ├── simple_adapter_chaining.py     # Przykład łańcuchowania adapterów
│   ├── dot_notation_example.py        # Przykład notacji kropkowej
│   ├── http_service_example.py        # Przykład serwera HTTP
│   └── ml_pipeline_example.py         # Przykład pipeline'u ML
│
├── tests/                             # Testy
│   ├── test_adapters/                 # Testy adapterów
│   ├── test_core/                     # Testy rdzenia
│   ├── test_emulators/                # Testy emulatorów
│   └── test_workflows/                # Testy workflow
│
├── data/                              # Katalog na dane
│   └── .gitkeep                       # Plik do zachowania pustego katalogu
│
├── models/                            # Katalog na modele ML
│   └── .gitkeep                       # Plik do zachowania pustego katalogu
│
├── output/                            # Katalog na wyniki
│   └── .gitkeep                       # Plik do zachowania pustego katalogu
│
├── docker/                            # Pliki Docker
│   ├── Dockerfile                     # Główny Dockerfile
│   ├── docker-compose.yml             # Kompozycja Docker
│   └── entrypoint.sh                  # Skrypt startowy
│
├── fonts/                             # Czcionki drukarek
│   ├── zpl/                           # Czcionki dla ZPL
│   ├── escpos/                        # Czcionki dla ESC/POS
│   └── pcl/                           # Czcionki dla PCL
│
├── .env                               # Zmienne środowiskowe
├── .gitignore                         # Ignorowane pliki dla Git
├── Makefile                           # Makefile z komendami
├── README.md                          # Dokumentacja projektu
├── requirements.txt                   # Zależności Pythona
├── setup.py                           # Skrypt instalacyjny
└── main.py                            # Punkt wejściowy