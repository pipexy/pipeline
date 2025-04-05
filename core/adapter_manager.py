# Zarządzanie adapterami
"""
adapter_manager.py
"""

"""
Moduł zarządzający adapterami w systemie.
"""

import os
import importlib
import inspect
from adapters.base import BaseAdapter


class AdapterManager:
    """
    Zarządza adapterami w systemie, umożliwiając ich dynamiczne ładowanie i rejestrację.
    """

    def __init__(self):
        """Inicjalizacja menedżera adapterów."""
        self.adapters = {}

    def register_adapter(self, adapter_id, adapter_instance):
        """
        Rejestruje adapter w systemie.

        Args:
            adapter_id: Identyfikator adaptera
            adapter_instance: Instancja adaptera

        Returns:
            AdapterManager: Instancja tego menedżera dla łańcuchowania metod
        """
        if not isinstance(adapter_instance, BaseAdapter):
            raise TypeError("Adapter must be an instance of BaseAdapter")

        self.adapters[adapter_id] = adapter_instance
        return self

    def get_adapter(self, adapter_id):
        """
        Pobiera adapter o podanym identyfikatorze.

        Args:
            adapter_id: Identyfikator adaptera

        Returns:
            BaseAdapter: Instancja adaptera lub None jeśli nie znaleziono
        """
        return self.adapters.get(adapter_id)

    def load_adapters_from_directory(self, directory):
        """
        Ładuje adaptery z podanego katalogu.

        Args:
            directory: Ścieżka do katalogu z adapterami

        Returns:
            AdapterManager: Instancja tego menedżera dla łańcuchowania metod
        """
        # Sprawdź czy katalog istnieje
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise ValueError(f"Directory not found: {directory}")

        # Przeszukaj katalog
        for filename in os.listdir(directory):
            # Tylko pliki .py
            if not filename.endswith('.py') or filename == '__init__.py':
                continue

            try:
                # Utwórz nazwę modułu
                module_name = filename[:-3]  # Usuń rozszerzenie .py

                # Zbuduj pełną ścieżkę do modułu
                module_path = os.path.join(directory, filename)

                # Załaduj moduł
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Znajdź wszystkie klasy dziedziczące po BaseAdapter
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                            issubclass(obj, BaseAdapter) and
                            obj != BaseAdapter):

                        # Utwórz ID adaptera
                        adapter_id = module_name
                        if adapter_id.endswith('_adapter'):
                            adapter_id = adapter_id[:-8]  # Usuń '_adapter'

                        # Utwórz instancję adaptera
                        adapter_instance = obj(adapter_id)

                        # Zarejestruj adapter
                        self.register_adapter(adapter_id, adapter_instance)
                        print(f"Registered adapter: {adapter_id}")

            except Exception as e:
                print(f"Error loading adapter from {filename}: {e}")

        return self

    def load_adapters_from_module(self, module_name):
        """
        Ładuje adaptery z podanego modułu.

        Args:
            module_name: Nazwa modułu

        Returns:
            AdapterManager: Instancja tego menedżera dla łańcuchowania metod
        """
        try:
            # Zaimportuj moduł
            module = importlib.import_module(module_name)

            # Pobierz wszystkie adaptery
            if hasattr(module, 'ADAPTERS'):
                for adapter_id, adapter in module.ADAPTERS.items():
                    self.register_adapter(adapter_id, adapter)

            return self

        except Exception as e:
            raise RuntimeError(f"Error loading adapters from module {module_name}: {e}")

    def get_all_adapters(self):
        """
        Zwraca wszystkie zarejestrowane adaptery.

        Returns:
            dict: Słownik adapterów (id -> instancja)
        """
        return self.adapters