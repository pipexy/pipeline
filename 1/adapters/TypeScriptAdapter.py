"""
TypeScriptAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class TypeScriptAdapter(ChainableAdapter):
    """Adapter for compiling and executing TypeScript code."""

    def code(self, ts_code):
        """Set TypeScript code to execute."""
        self._params['code'] = ts_code
        return self

    def file(self, file_path):
        """Set TypeScript file to execute."""
        self._params['file'] = file_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        ts_file = None
        input_file = None
        js_file = None
        temp_dir = None

        try:
            # Handle input data
            if input_data:
                with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                    if isinstance(input_data, (dict, list)):
                        json.dump(input_data, f)
                    else:
                        f.write(str(input_data))
                    input_file = f.name

            # Create temp directory for compilation
            temp_dir = tempfile.mkdtemp()

            # Get the TypeScript code or file
            code = self._params.get('code')
            file_path = self._params.get('file')

            if not code and not file_path:
                raise ValueError("TypeScript adapter requires either 'code' or 'file' parameter")

            if code:
                # Create a TypeScript file
                ts_file = os.path.join(temp_dir, "script.ts")

                # Add input handling wrapper
                wrapper_code = """
                import * as fs from 'fs';

                let input = null;
                if (process.argv.length > 2) {
                    try {
                        const inputFile = process.argv[2];
                        const content = fs.readFileSync(inputFile, 'utf8');
                        try {
                            input = JSON.parse(content);
                        } catch (e) {
                            input = content;
                        }
                    } catch (e) {
                        console.error('Error reading input file:', e);
                    }
                }

                // User code starts here
                %s
                """

                with open(ts_file, 'w') as f:
                    f.write(wrapper_code % code)
            else:
                # Use existing file
                ts_file = file_path

            # Compile TypeScript to JavaScript
            js_file = ts_file.replace('.ts', '.js')
            compile_result = subprocess.run(
                f"tsc {ts_file} --target ES2020 --module CommonJS",
                shell=True,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"TypeScript compilation failed: {compile_result.stderr}")

            # Execute the compiled JS
            cmd = f"node {js_file}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"TypeScript execution failed: {run_result.stderr}")

            # Return the output
            output = run_result.stdout.strip()

            # Try parsing as JSON if it looks like JSON
            if output.startswith('{') or output.startswith('['):
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    pass

            return output

        finally:
            # Clean up temporary files
            import shutil
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self