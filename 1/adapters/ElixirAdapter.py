"""
ElixirAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class ElixirAdapter(ChainableAdapter):
    """Adapter for executing Elixir code."""

    def code(self, elixir_code):
        """Set Elixir code to execute."""
        self._params['code'] = elixir_code
        return self

    def script(self, script_path):
        """Set Elixir script path to execute."""
        self._params['script'] = script_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        elixir_file = None
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

            # Get the Elixir code/script
            code = self._params.get('code')
            script = self._params.get('script')

            if not code and not script:
                raise ValueError("Elixir adapter requires either 'code' or 'script' parameter")

            if code:
                # Create an Elixir file with input handling wrapper
                with tempfile.NamedTemporaryFile(suffix=".exs", delete=False, mode='w+') as f:
                    wrapper_code = """
                    # Read input data if available
                    input_data = case System.argv() do
                      [input_file] ->
                        if File.exists?(input_file) do
                          case File.read(input_file) do
                            {:ok, content} ->
                              try do
                                Jason.decode!(content)
                              rescue
                                _ -> content
                              end
                            _ -> nil
                          end
                        else
                          nil
                        end
                      _ -> nil
                    end

                    # User code starts here
                    %s
                    """
                    f.write(wrapper_code % code)
                    elixir_file = f.name
            else:
                # Use the provided script
                elixir_file = script

            # Execute the Elixir script
            cmd = f"elixir {elixir_file}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"Elixir execution failed: {run_result.stderr}")

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
            if elixir_file and os.path.exists(elixir_file) and 'script' not in self._params:
                os.unlink(elixir_file)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self