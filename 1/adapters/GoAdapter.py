"""
GoAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class GoAdapter(ChainableAdapter):
    """Adapter for compiling and executing Go code."""

    def code(self, go_code):
        """Set Go code to execute."""
        self._params['code'] = go_code
        return self

    def file(self, file_path):
        """Set Go file to execute."""
        self._params['file'] = file_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        go_file = None
        input_file = None
        temp_dir = None

        try:
            # Create temp directory for Go modules
            temp_dir = tempfile.mkdtemp()

            # Handle input data
            if input_data:
                with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                    if isinstance(input_data, (dict, list)):
                        json.dump(input_data, f)
                    else:
                        f.write(str(input_data))
                    input_file = f.name

            # Get the Go code or file
            code = self._params.get('code')
            file_path = self._params.get('file')

            if not code and not file_path:
                raise ValueError("Go adapter requires either 'code' or 'file' parameter")

            if code:
                # Create a Go file with input handling wrapper
                go_file = os.path.join(temp_dir, "main.go")

                wrapper_code = """
                package main

                import (
                    "encoding/json"
                    "fmt"
                    "io/ioutil"
                    "os"
                )

                func main() {
                    // Read input data if provided
                    var inputData interface{}
                    if len(os.Args) > 1 {
                        inputFile := os.Args[1]
                        data, err := ioutil.ReadFile(inputFile)
                        if err == nil {
                            // Try to parse as JSON
                            json.Unmarshal(data, &inputData)
                        }
                    }

                    // User code starts here
                    %s
                }
                """

                with open(go_file, 'w') as f:
                    f.write(wrapper_code % code)
            else:
                # Use existing file
                go_file = file_path

            # Initialize Go module if using code
            if 'code' in self._params:
                init_cmd = f"cd {temp_dir} && go mod init example.com/goapp"
                init_result = subprocess.run(
                    init_cmd,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if init_result.returncode != 0:
                    raise RuntimeError(f"Go module initialization failed: {init_result.stderr}")

            # Execute Go file
            if 'code' in self._params:
                cmd = f"cd {temp_dir} && go run main.go"
            else:
                cmd = f"go run {go_file}"

            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"Go execution failed: {run_result.stderr}")

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
            if temp_dir and os.path.exists(temp_dir) and 'code' in self._params:
                shutil.rmtree(temp_dir)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self