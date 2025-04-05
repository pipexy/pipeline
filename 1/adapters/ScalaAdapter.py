"""
ScalaAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class ScalaAdapter(ChainableAdapter):
    """Adapter for compiling and executing Scala code."""

    def code(self, scala_code):
        """Set Scala code to execute."""
        self._params['code'] = scala_code
        return self

    def file(self, file_path):
        """Set Scala file to execute."""
        self._params['file'] = file_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        scala_file = None
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

            # Get the Scala code or file
            code = self._params.get('code')
            file_path = self._params.get('file')

            if not code and not file_path:
                raise ValueError("Scala adapter requires either 'code' or 'file' parameter")

            if code:
                # Create a Scala file with input handling wrapper
                with tempfile.NamedTemporaryFile(suffix=".scala", delete=False, mode='w+') as f:
                    wrapper_code = """
                    import scala.io.Source
                    import scala.util.Try
                    import scala.util.parsing.json._

                    object Main {
                        // Function to read input data
                        def readInput(): Option[String] = {
                            if (args.length > 0) {
                                Try {
                                    val source = Source.fromFile(args(0))
                                    val content = source.mkString
                                    source.close()
                                    Some(content)
                                }.getOrElse(None)
                            } else None
                        }

                        // Parse JSON input if possible
                        def parseJsonInput(): Option[Any] = {
                            readInput().flatMap(input => JSON.parseFull(input))
                        }

                        // Main method
                        def main(args: Array[String]): Unit = {
                            // Input is available via readInput() or parseJsonInput()
                            
                            // User code starts here
                            %s
                        }
                    }
                    """
                    f.write(wrapper_code % code)
                    scala_file = f.name
            else:
                # Use the provided file
                scala_file = file_path

            # Execute the Scala code
            cmd = f"scala {scala_file}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"Scala execution failed: {run_result.stderr}")

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
            if scala_file and os.path.exists(scala_file) and 'file' not in self._params:
                os.unlink(scala_file)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self