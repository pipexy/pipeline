"""
PHPAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class PHPAdapter(ChainableAdapter):
    """Adapter for executing PHP code."""

    def code(self, php_code):
        """Set PHP code to execute."""
        self._params['code'] = php_code
        return self

    def script(self, script_path):
        """Set PHP script path to execute."""
        self._params['script'] = script_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        php_file = None
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

            # Get the PHP code/script
            code = self._params.get('code')
            script = self._params.get('script')

            if not code and not script:
                raise ValueError("PHP adapter requires either 'code' or 'script' parameter")

            if code:
                # Create a PHP file with wrapper for input handling
                with tempfile.NamedTemporaryFile(suffix=".php", delete=False, mode='w+') as f:
                    wrapper_code = """<?php
                    // Parse input if available
                    $input_data = null;
                    if ($argc > 1) {
                        $input_path = $argv[1];
                        if (file_exists($input_path)) {
                            $content = file_get_contents($input_path);
                            // Try to parse as JSON
                            $json_data = json_decode($content, true);
                            if (json_last_error() === JSON_ERROR_NONE) {
                                $input_data = $json_data;
                            } else {
                                $input_data = $content;
                            }
                        }
                    }

                    // User code starts here
                    %s
                    ?>"""
                    f.write(wrapper_code % code)
                    php_file = f.name
            else:
                # Use the provided script path
                php_file = script

            # Execute PHP file
            cmd = f"php {php_file}"
            if input_file:
                cmd += f" {input_file}"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"PHP execution failed: {result.stderr}")

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
            if php_file and os.path.exists(php_file) and 'script' not in self._params:
                os.unlink(php_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self