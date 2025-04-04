# api_server.py
from flask import Flask, request, jsonify
from pipeline_engine import PipelineEngine
from dsl_parser import YamlDSLParser

app = Flask(__name__)


@app.route('/execute', methods=['POST'])
def execute_pipeline():
    data = request.json

    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    # Pobierz pipeline i dane wejściowe
    pipeline_expr = data.get('pipeline')
    yaml_content = data.get('yaml')
    pipeline_name = data.get('pipeline_name')
    input_data = data.get('input')

    if not pipeline_expr and not yaml_content:
        return jsonify({'error': 'Either pipeline or yaml must be provided'}), 400

    try:
        # Wykonaj pipeline
        if pipeline_expr:
            result = PipelineEngine.execute_from_dot_notation(pipeline_expr, input_data)
        else:
            result = PipelineEngine.execute_from_yaml(yaml_content, pipeline_name, input_data)

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)