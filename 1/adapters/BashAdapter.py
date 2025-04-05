"""
BashAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class BashAdapter(ChainableAdapter):
    """Adapter for executing Bash scripts."""

    def command(self, cmd):
        """Set command to execute."""
        self._params['command'] = cmd
        return self

    def script(self, script_content):
        """Set script content to execute."""
        self._params['script'] = script_content
        return self

    def file(self, file_path):
        """Set script file to execute."""
        self._params['file'] = file_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        script_file = None
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

            # Get the command, script or file
            command = self._params.get('command')
            script = self._params.get('script')
            file_path = self._params.get('file')

            if command:
                # Direct command execution
                if input_file:
                    cmd = f"{command} {input_file}"
                else:
                    cmd = command

            elif script:
                # Create a script file with content
                with tempfile.NamedTemporaryFile(suffix=".sh", delete=False, mode='w+') as f:
                    f.write("#!/bin/bash\n")
                    f.write(script)
                    script_file = f.name
                os.chmod(script_file, 0o755)

                cmd = script_file
                if input_file:
                    cmd += f" {input_file}"

            elif file_path:
                # Use existing script file
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Script file not found: {file_path}")
                os.chmod(file_path, 0o755)

                cmd = file_path
                if input_file:
                    cmd += f" {input_file}"

            else:
                raise ValueError("BashAdapter requires one of 'command', 'script', or 'file' parameters")

            # Execute the command
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            # Check for errors
            if result.returncode != 0 and 'ignore_errors' not in self._params:
                raise RuntimeError(f"Bash execution failed: {result.stderr}")

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
            if script_file and os.path.exists(script_file) and 'script' in self._params:
                os.unlink(script_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self