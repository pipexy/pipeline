"""
R_Adapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class R_Adapter(ChainableAdapter):
    """Adapter for executing R code."""

    def code(self, r_code):
        """Set R code to execute."""
        self._params['code'] = r_code
        return self

    def script(self, script_path):
        """Set R script path to execute."""
        self._params['script'] = script_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        r_file = None
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

            # Get the R code/script
            code = self._params.get('code')
            script = self._params.get('script')

            if not code and not script:
                raise ValueError("R adapter requires either 'code' or 'script' parameter")

            if code:
                # Create an R file with input handling wrapper
                with tempfile.NamedTemporaryFile(suffix=".R", delete=False, mode='w+') as f:
                    wrapper_code = """
                    # Parse command line arguments
                    args <- commandArgs(trailingOnly = TRUE)
                    input_data <- NULL

                    # Read input data if available
                    if (length(args) > 0) {
                      input_file <- args[1]
                      if (file.exists(input_file)) {
                        # Try to read as JSON first
                        tryCatch({
                          input_data <- jsonlite::fromJSON(input_file)
                        }, error = function(e) {
                          # Fall back to plain text
                          input_data <- readLines(input_file, warn = FALSE)
                          if (length(input_data) == 1) {
                            input_data <- input_data[1]
                          }
                        })
                      }
                    }

                    # User code starts here
                    %s
                    """
                    f.write(wrapper_code % code)
                    r_file = f.name
            else:
                # Use the provided script path
                r_file = script

            # Execute the R script
            cmd = f"Rscript {r_file}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"R execution failed: {run_result.stderr}")

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
            if r_file and os.path.exists(r_file) and 'script' not in self._params:
                os.unlink(r_file)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self