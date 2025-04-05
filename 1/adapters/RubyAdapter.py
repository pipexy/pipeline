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

            # Get the Ruby code
            code = self._params.get('code')
            if not code:
                raise ValueError("Ruby adapter requires 'code' method")

            # Create a Ruby file
            with tempfile.NamedTemporaryFile(suffix=".rb", delete=False, mode='w+') as f:
                # Wrapping to handle input
                wrapper_code = """
                require 'json'

                input = nil
                if ARGV.length > 0
                  begin
                    content = File.read(ARGV[0])
                    begin
                      input = JSON.parse(content)
                    rescue
                      input = content
                    end
                  rescue => e
                    STDERR.puts "Error reading input file: #{e.message}"
                  end
                end

                # User code starts here
                %s
                """
                f.write(wrapper_code % code)
                ruby_file = f.name

            # Execute Ruby file
            cmd = f"ruby {ruby_file}"
            if input_file:
                cmd += f" {input_file}"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Ruby execution failed: {result.stderr}")

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
            if ruby_file and os.path.exists(ruby_file):
                os.unlink(ruby_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self