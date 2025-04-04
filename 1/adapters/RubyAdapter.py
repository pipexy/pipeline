"""
RubyAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class RubyAdapter(ChainableAdapter):
    """Adapter for executing Ruby code."""

    def code(self, ruby_code):
        """Set Ruby code to execute."""
        self._params['code'] = ruby_code
        return self

    def script(self, script_path):
        """Set Ruby script path to execute."""
        self._params['script'] = script_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        ruby_file = None
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

            # Get the Ruby code/script
            code = self._params.get('code')
            script = self._params.get('script')

            if not code and not script:
                raise ValueError("Ruby adapter requires either 'code' or 'script' parameter")

            if code:
                # Create a Ruby file with input handling wrapper
                with tempfile.NamedTemporaryFile(suffix=".rb", delete=False, mode='w+') as f:
                    wrapper_code = """
                    require 'json'

                    # Read input data if available
                    input_data = nil
                    if ARGV.length > 0
                      input_file = ARGV[0]
                      if File.exist?(input_file)
                        begin
                          input_text = File.read(input_file)
                          input_data = JSON.parse(input_text) rescue input_text
                        rescue => e
                          STDERR.puts "Warning: Failed to read input file: #{e.message}"
                        end
                      end
                    end

                    # User code starts here
                    %s
                    """
                    f.write(wrapper_code % code)
                    ruby_file = f.name
            else:
                # Use the provided script
                ruby_file = script

            # Execute the Ruby code
            cmd = f"ruby {ruby_file}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"Ruby execution failed: {run_result.stderr}")

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
            if ruby_file and os.path.exists(ruby_file) and 'script' not in self._params:
                os.unlink(ruby_file)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self