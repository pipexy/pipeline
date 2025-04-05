"""
GoAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class GoAdapter(ChainableAdapter):
    """Adapter for executing Go code."""

    def _execute_self(self, input_data=None):
        # Create temporary files
        go_file = None
        input_file = None
        compiled_file = None

        try:
            # Handle input data
            if input_data:
                with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                    if isinstance(input_data, (dict, list)):
                        json.dump(input_data, f)
                    else:
                        f.write(str(input_data))
                    input_file = f.name

            # Get the Go code
            code = self._params.get('code')
            if not code:
                raise ValueError("Go adapter requires 'code' method")

            # Create a Go file
            with tempfile.NamedTemporaryFile(suffix=".go", delete=False, mode='w+') as f:
                # If no package main, wrap in a main package
                if "package main" not in code:
                    wrapped_code = """
                    package main

                    import (
                        "encoding/json"
                        "fmt"
                        "io/ioutil"
                        "os"
                    )

                    func main() {
                        var input interface{}
                        
                        if len(os.Args) > 1 {
                            content, err := ioutil.ReadFile(os.Args[1])
                            if err == nil {
                                // Try to parse as JSON
                                err = json.Unmarshal(content, &input)
                                if err != nil {
                                    // If not JSON, use as string
                                    input = string(content)
                                }
                            }
                        }
                        
                        // User code starts here
                        %s
                    }
                    """
                    f.write(wrapped_code % code)
                else:
                    f.write(code)

                go_file = f.name

            # Create a temporary name for the compiled executable
            compiled_file = f"{go_file}_bin"

            # Compile the Go code
            compile_cmd = f"go build -o {compiled_file} {go_file}"
            compile_result = subprocess.run(
                compile_cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"Go compilation failed: {compile_result.stderr}")

            # Execute the compiled Go program
            exec_cmd = f"{compiled_file}"
            if input_file:
                exec_cmd += f" {input_file}"

            result = subprocess.run(
                exec_cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Go execution failed: {result.stderr}")

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
            if go_file and os.path.exists(go_file):
                os.unlink(go_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

            if compiled_file and os.path.exists(compiled_file):
                os.unlink(compiled_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self