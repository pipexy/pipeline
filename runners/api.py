# Serwer API
"""
api.py
"""

"""
Serwer API dla systemu emulatorów drukarek.
"""

import os
import json
import time
from flask import Flask, request, jsonify, send_file
import tempfile
from core.pipeline_engine import PipelineEngine
from core.workflow_engine import WorkflowEngine
from adapters import ADAPTERS
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Inicjalizacja silników
workflow_engine = WorkflowEngine()

# Ładowanie workflow
workflow_dir = os.path.join(os.getcwd(), 'workflows')
if os.path.exists(workflow_dir):
    for filename in os.listdir(workflow_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            try:
                workflow_path = os.path.join(workflow_dir, filename)
                workflow_id = workflow_engine.load_workflow(workflow_path)
                print(f"Loaded workflow: {workflow_id}")
            except Exception as e:
                print(f"Error loading workflow {filename}: {e}")


@app.route('/api/adapters', methods=['GET'])
def list_adapters():
    """Zwraca listę dostępnych adapterów."""
    adapters = []

    for adapter_id, adapter in ADAPTERS.items():
        adapters.append({
            'id': adapter_id,
            'name': adapter.name or adapter_id,
            'type': adapter.__class__.__name__
        })

    return jsonify(adapters)


@app.route('/api/execute', methods=['POST'])
def execute_pipeline():
    """Wykonuje pipeline z ciała żądania."""
    data = request.json

    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    # Przygotowanie danych
    pipeline_expr = data.get('pipeline')
    input_data = data.get('input')

    if not pipeline_expr:
        return jsonify({'error': 'Pipeline expression not provided'}), 400

    try:
        # Wykonanie pipeline'a
        result = PipelineEngine.execute_from_dot_notation(pipeline_expr, input_data)

        # Jeśli wynik zawiera dane binarne, zapisz je do pliku tymczasowego
        if isinstance(result, dict) and ('image_data' in result or 'image' in result):
            # Dane binarne w result['image_data'] lub obiekt PIL w result['image']
            image_data = result.get('image_data')
            image = result.get('image')

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                if image_data:
                    tmp.write(image_data)
                elif image:
                    image.save(tmp.name)
                else:
                    return jsonify({'error': 'No image data found in result'}), 500

                # Dodaj ścieżkę do pliku w wyniku
                result['temp_file'] = tmp.name

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflow/<workflow_id>', methods=['POST'])
def execute_workflow(workflow_id):
    """Wykonuje workflow o podanym ID."""
    if workflow_id not in workflow_engine.workflows:
        return jsonify({'error': f'Workflow not found: {workflow_id}'}), 404

    # Pobierz dane wejściowe
    input_data = request.json or {}

    try:
        # Wykonaj workflow
        context = workflow_engine.execute_workflow(workflow_id, input_data)

        # Zwróć wyniki
        return jsonify({
            'outputs': context.get('outputs', {}),
            'metadata': {
                'workflow_id': workflow_id,
                'execution_time': time.time(),
                'step_count': len(context.get('steps', {}))
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflows', methods=['GET'])
def list_workflows():
    """Zwraca listę dostępnych workflow."""
    workflows = []

    for workflow_id, workflow in workflow_engine.workflows.items():
        workflows.append({
            'id': workflow_id,
            'name': workflow.get('name', workflow_id),
            'description': workflow.get('description', ''),
            'version': workflow.get('version', '1.0')
        })

    return jsonify(workflows)


@app.route('/api/emulate/zpl', methods=['POST'])
def emulate_zpl():
    """Emuluje wydruk kodu ZPL."""
    zpl_code = request.data.decode('utf-8')

    # Parametry z query string
    dpi = request.args.get('dpi', 203, type=int)
    width = request.args.get('width', 4, type=float)
    height = request.args.get('height', 6, type=float)

    try:
        # Wykonaj emulację
        result = ADAPTERS['zpl'].render_mode('labelary').dpi(dpi).width(width).height(height).execute(zpl_code)

        # Zwróć obraz jako odpowiedź
        if 'image_data' in result:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.write(result['image_data'])
            temp_file.close()

            return send_file(temp_file.name,
                             mimetype='image/png',
                             as_attachment=True,
                             download_name='zpl_output.png')
        else:
            return jsonify({'error': 'No image generated'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/emulate/escpos', methods=['POST'])
def emulate_escpos():
    """Emuluje wydruk poleceń ESC/POS."""
    escpos_data = request.data

    # Parametry z query string
    width = request.args.get('width', 80, type=int)
    dpi = request.args.get('dpi', 203, type=int)

    try:
        # Wykonaj emulację
        result = ADAPTERS['escpos'].width(width).dpi(dpi).execute(escpos_data)

        # Zwróć obraz jako odpowiedź
        if 'image' in result:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.close()

            result['image'].save(temp_file.name)

            return send_file(temp_file.name,
                             mimetype='image/png',
                             as_attachment=True,
                             download_name='escpos_output.png')
        else:
            return jsonify({'error': 'No image generated'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Obsługuje przesyłanie pliku i wykonuje odpowiedni emulator."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        emulator_type = request.form.get('emulator', '').lower()

        # Zapisz plik tymczasowo
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)
        temp_file.close()

        try:
            # Wybierz emulator na podstawie typu lub rozszerzenia pliku
            if not emulator_type:
                if filename.endswith('.zpl'):
                    emulator_type = 'zpl'
                elif filename.endswith('.prn') or filename.endswith('.bin'):
                    emulator_type = 'escpos'
                elif filename.endswith('.pcl'):
                    emulator_type = 'pcl'
                else:
                    return jsonify({'error': 'Could not determine emulator type from file extension'}), 400

            # Sprawdź czy emulator istnieje
            if emulator_type not in ADAPTERS:
                return jsonify({'error': f'Unknown emulator type: {emulator_type}'}), 400

            # Wczytaj dane z pliku
            with open(temp_file.name, 'rb') as f:
                file_data = f.read()

            # Parametry z formularza
            dpi = request.form.get('dpi', 203, type=int)
            width = request.form.get('width', 4, type=float)
            height = request.form.get('height', 6, type=float)

            # Wykonaj emulację
            adapter = ADAPTERS[emulator_type]

            # Skonfiguruj adapter
            if emulator_type == 'zpl':
                adapter.render_mode('labelary').dpi(dpi).width(width).height(height)
            elif emulator_type == 'escpos':
                adapter.width(width).dpi(dpi)
            elif emulator_type == 'pcl':
                adapter.mode('ghostscript').dpi(dpi)

            # Wykonaj emulację
            result = adapter.execute(file_data)

            # Utwórz plik wynikowy
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            output_file.close()

            # Zapisz wynik
            if 'image_data' in result:
                with open(output_file.name, 'wb') as f:
                    f.write(result['image_data'])
            elif 'image' in result:
                result['image'].save(output_file.name)
            else:
                return jsonify({'error': 'No image generated'}), 500

            # Zwróć obraz
            return send_file(output_file.name,
                             mimetype='image/png',
                             as_attachment=True,
                             download_name=f'{os.path.splitext(filename)[0]}_output.png')

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Usuń plik tymczasowy
            os.unlink(temp_file.name)


def run_server(host='0.0.0.0', port=5000):
    """Uruchamia serwer API."""
    app.run(host=host, port=port)


if __name__ == '__main__':
    run_server()