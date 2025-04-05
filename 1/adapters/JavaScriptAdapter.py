"""
JavaScriptAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class JavaScriptAdapter(ChainableAdapter):
    """Adapter for executing JavaScript code in browsers or other environments."""

    def _execute_self(self, input_data=None):
        # Create temporary files
        js_file = None
        input_file = None

        try:
            # Handle input data
            if input_data:
                with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                    if isinstance(input_data, (dict, list)):
                        json.dump(input_data, f)
                    else:
                        f.write(str(input_data))
                    input_file = f.name

            # Get the JavaScript code
            code = self._params.get('code')
            engine = self._params.get('engine', 'node')  # Default to node if not specified

            if not code:
                raise ValueError("JavaScript adapter requires 'code' method")

            # Create a JavaScript file
            with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode='w+') as f:
                # Wrapping to handle input
                wrapper_code = """
                const fs = require('fs');
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
                f.write(wrapper_code % code)
                js_file = f.name

            # Execute JavaScript file
            cmd = f"{engine} {js_file}"
            if input_file:
                cmd += f" {input_file}"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"JavaScript execution failed: {result.stderr}")

            # Return the output
            output = result.stdout.strip()

            # Try parsing as JSON if it looks like JSON
            if output.startswith('{') or output.startswith('['):
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    pass

            return output

        finally:
            # Clean up temporary files
            if js_file and os.path.exists(js_file):
                os.unlink(js_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self