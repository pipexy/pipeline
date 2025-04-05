# Adapter dla Machine Learning
"""
ml_adapter.py
"""

# ml_adapter.py
from adapters_extended import ChainableAdapter
import json
import tempfile
import os
import pickle


class MLAdapter(ChainableAdapter):
    """Adapter do wykonywania operacji związanych z Machine Learning."""

    def _execute_self(self, input_data=None):
        operation = self._params.get('operation', 'predict')

        if operation == 'predict':
            return self._predict(input_data)
        elif operation == 'train':
            return self._train(input_data)
        elif operation == 'evaluate':
            return self._evaluate(input_data)
        elif operation == 'analyze':
            return self._analyze(input_data)
        else:
            raise ValueError(f"Unsupported ML operation: {operation}")

    def _predict(self, input_data):
        # Sprawdź, czy podano model
        model_path = self._params.get('model_path')
        if not model_path:
            raise ValueError("ML adapter requires 'model_path' parameter for predict operation")

        # Załaduj model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        # Wykonaj predykcję
        try:
            import numpy as np
            import pandas as pd

            # Konwersja danych wejściowych
            if isinstance(input_data, list):
                if all(isinstance(x, dict) for x in input_data):
                    # Lista słowników -> DataFrame
                    X = pd.DataFrame(input_data)
                else:
                    # Lista wartości -> numpy array
                    X = np.array(input_data)
            elif isinstance(input_data, dict):
                # Jeden słownik -> DataFrame z jednym wierszem
                X = pd.DataFrame([input_data])
            else:
                X = input_data

            # Predykcja
            predictions = model.predict(X)

            # Próba uzyskania prawdopodobieństw
            probabilities = None
            if hasattr(model, 'predict_proba'):
                try:
                    probabilities = model.predict_proba(X)
                except:
                    pass

            # Formatowanie wyniku
            result = {}

            if isinstance(X, pd.DataFrame):
                # Dla DataFrame, zwróć predykcje jako listę
                result['predictions'] = predictions.tolist()

                if probabilities is not None:
                    result['probabilities'] = probabilities.tolist()

                # Dodaj oryginalne dane
                if self._params.get('include_input', False):
                    result['input_data'] = X.to_dict('records')
            else:
                # Dla pojedynczej próbki
                result['prediction'] = predictions.tolist() if hasattr(predictions, 'tolist') else predictions

                if probabilities is not None:
                    result['probability'] = probabilities.tolist() if hasattr(probabilities,
                                                                              'tolist') else probabilities

            return result

        except Exception as e:
            raise RuntimeError(f"Error making prediction: {e}")

    def _train(self, input_data):
        # Sprawdź, czy podano dane wejściowe
        if not input_data:
            raise ValueError("Input data required for training")

        try:
            import numpy as np
            import pandas as pd
            from sklearn.model_selection import train_test_split

            # Parametry treningu
            test_size = self._params.get('test_size', 0.2)
            random_state = self._params.get('random_state', 42)
            model_type = self._params.get('model_type', 'linear_regression')
            target_column = self._params.get('target_column')

            if not target_column:
                raise ValueError("Parameter 'target_column' is required for training")

            # Konwersja danych wejściowych
            if isinstance(input_data, list) and all(isinstance(x, dict) for x in input_data):
                df = pd.DataFrame(input_data)
            elif isinstance(input_data, str) and (input_data.endswith('.csv') or input_data.endswith('.tsv')):
                # Odczytaj z pliku
                separator = '\t' if input_data.endswith('.tsv') else ','
                df = pd.read_csv(input_data, sep=separator)
            else:
                raise ValueError("Input data must be a list of dictionaries or a path to a CSV/TSV file")

            # Przygotuj dane
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in data")

            X = df.drop(columns=[target_column])
            y = df[target_column]

            # Podział na zbiór treningowy i testowy
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )

            # Wybór i trening modelu
            model = self._get_model(model_type)
            model.fit(X_train, y_train)

            # Ewaluacja modelu
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)

            # Zapisz model
            output_path = self._params.get('output_path')
            if output_path:
                with open(output_path, 'wb') as f:
                    pickle.dump(model, f)

            return {
                'success': True,
                'model_type': model_type,
                'train_score': train_score,
                'test_score': test_score,
                'n_samples': len(df),
                'n_features': X.shape[1],
                'model_path': output_path
            }

        except Exception as e:
            raise RuntimeError(f"Error training model: {e}")

    def _evaluate(self, input_data):
        # Sprawdź, czy podano model i dane
        model_path = self._params.get('model_path')
        if not model_path:
            raise ValueError("ML adapter requires 'model_path' parameter for evaluate operation")

        try:
            import numpy as np
            import pandas as pd
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, f1_score,
                mean_squared_error, r2_score, confusion_matrix
            )

            # Załaduj model
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            # Konwersja danych wejściowych
            if isinstance(input_data, list) and all(isinstance(x, dict) for x in input_data):
                df = pd.DataFrame(input_data)
            elif isinstance(input_data, str) and (input_data.endswith('.csv') or input_data.endswith('.tsv')):
                # Odczytaj z pliku
                separator = '\t' if input_data.endswith('.tsv') else ','
                df = pd.read_csv(input_data, sep=separator)
            else:
                raise ValueError("Input data must be a list of dictionaries or a path to a CSV/TSV file")

            # Przygotuj dane
            target_column = self._params.get('target_column')
            if not target_column:
                raise ValueError("Parameter 'target_column' is required for evaluation")

            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in data")

            X = df.drop(columns=[target_column])
            y_true = df[target_column]

            # Predykcja
            y_pred = model.predict(X)

            # Wybór metryk w zależności od typu modelu
            is_classifier = hasattr(model, 'classes_')

            if is_classifier:
                # Metryki dla klasyfikacji
                metrics = {
                    'accuracy': accuracy_score(y_true, y_pred),
                    'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
                    'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
                    'f1': f1_score(y_true, y_pred, average='weighted', zero_division=0),
                    'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
                }
            else:
                # Metryki dla regresji
                metrics = {
                    'mse': mean_squared_error(y_true, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                    'r2': r2_score(y_true, y_pred),
                    'mean_error': np.mean(np.abs(y_true - y_pred))
                }

            return {
                'success': True,
                'model_type': type(model).__name__,
                'n_samples': len(df),
                'metrics': metrics,
                'is_classifier': is_classifier
            }

        except Exception as e:
            raise RuntimeError(f"Error evaluating model: {e}")

    def _analyze(self, input_data):
        try:
            import pandas as pd
            import numpy as np
            from scipy import stats

            # Konwersja danych wejściowych
            if isinstance(input_data, list) and all(isinstance(x, dict) for x in input_data):
                df = pd.DataFrame(input_data)
            elif isinstance(input_data, str) and (input_data.endswith('.csv') or input_data.endswith('.tsv')):
                # Odczytaj z pliku
                separator = '\t' if input_data.endswith('.tsv') else ','
                df = pd.read_csv(input_data, sep=separator)
            else:
                raise ValueError("Input data must be a list of dictionaries or a path to a CSV/TSV file")

            # Podstawowa analiza danych
            analysis = {
                'n_rows': len(df),
                'n_columns': len(df.columns),
                'columns': list(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'column_types': df.dtypes.astype(str).to_dict()
            }

            # Analiza statystyczna
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            if len(numeric_columns) > 0:
                # Statystyki dla kolumn numerycznych
                stats_dict = {}
                for col in numeric_columns:
                    col_stats = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median()),
                        'std': float(df[col].std()),
                        'skew': float(stats.skew(df[col].dropna()))
                    }
                    stats_dict[col] = col_stats

                analysis['numeric_stats'] = stats_dict

            # Analiza kategoryczna
            categorical_columns = df.select_dtypes(include=['object']).columns

            if len(categorical_columns) > 0:
                # Statystyki dla kolumn kategorycznych
                cat_stats = {}
                for col in categorical_columns:
                    value_counts = df[col].value_counts().to_dict()
                    cat_stats[col] = {
                        'unique_values': len(value_counts),
                        'top_values': dict(sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
                        'null_count': int(df[col].isnull().sum())
                    }

                analysis['categorical_stats'] = cat_stats

            # Korelacja między kolumnami numerycznymi
            if len(numeric_columns) > 1:
                corr_matrix = df[numeric_columns].corr().round(3)

                # Znajdź silne korelacje (abs > 0.7)
                strong_corr = []
                for i in range(len(numeric_columns)):
                    for j in range(i + 1, len(numeric_columns)):
                        col1 = numeric_columns[i]
                        col2 = numeric_columns[j]
                        corr_val = corr_matrix.iloc[i, j]

                        if abs(corr_val) > 0.7:
                            strong_corr.append({
                                'column1': col1,
                                'column2': col2,
                                'correlation': float(corr_val)
                            })

                analysis['correlation'] = {
                    'matrix': corr_matrix.to_dict(),
                    'strong_correlations': strong_corr
                }

            return analysis

        except Exception as e:
            raise RuntimeError(f"Error analyzing data: {e}")

    def _get_model(self, model_type):
        """Zwraca instancję modelu na podstawie podanego typu."""
        try:
            from sklearn.linear_model import LinearRegression, LogisticRegression
            from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
            from sklearn.svm import SVR, SVC
            from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier

            model_params = self._params.get('model_params', {})

            if model_type == 'linear_regression':
                return LinearRegression(**model_params)
            elif model_type == 'logistic_regression':
                return LogisticRegression(**model_params)
            elif model_type == 'random_forest_regressor':
                return RandomForestRegressor(**model_params)
            elif model_type == 'random_forest_classifier':
                return RandomForestClassifier(**model_params)
            elif model_type == 'svr':
                return SVR(**model_params)
            elif model_type == 'svc':
                return SVC(**model_params)
            elif model_type == 'knn_regressor':
                return KNeighborsRegressor(**model_params)
            elif model_type == 'knn_classifier':
                return KNeighborsClassifier(**model_params)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

        except ImportError:
            raise ImportError("scikit-learn is required for ML operations. Install with: pip install scikit-learn")


# Dodaj adapter do dostępnych adapterów
ml = MLAdapter('ml')
ADAPTERS['ml'] = ml