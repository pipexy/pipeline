"""
KotlinAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class KotlinAdapter(ChainableAdapter):
    """Adapter for compiling and executing Kotlin code."""

    def code(self, kotlin_code):
        """Set Kotlin code to execute."""
        self._params['code'] = kotlin_code
        return self

    def file(self, file_path):
        """Set Kotlin file to execute."""
        self._params['file'] = file_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        kotlin_file = None
        input_file = None
        jar_file = None

        try:
            # Handle input data
            if input_data:
                with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                    if isinstance(input_data, (dict, list)):
                        json.dump(input_data, f)
                    else:
                        f.write(str(input_data))
                    input_file = f.name

            # Get the Kotlin code or file
            code = self._params.get('code')
            file_path = self._params.get('file')

            if not code and not file_path:
                raise ValueError("Kotlin adapter requires either 'code' or 'file' parameter")

            # Create temp directory for compilation
            temp_dir = tempfile.mkdtemp()

            if code:
                # Create a Kotlin file with input handling wrapper
                kotlin_file = os.path.join(temp_dir, "Main.kt")

                wrapper_code = """
                import java.io.File
                import kotlinx.serialization.*
                import kotlinx.serialization.json.*

                // Function to read input data
                fun readInput(): String? {
                    if (args.isNotEmpty()) {
                        try {
                            return File(args[0]).readText()
                        } catch (e: Exception) {
                            println("Error reading input file: ${e.message}")
                        }
                    }
                    return null
                }

                // User code starts here
                %s
                """

                with open(kotlin_file, 'w') as f:
                    f.write(wrapper_code % code)
            else:
                kotlin_file = file_path

            # Compile Kotlin code
            jar_file = os.path.join(temp_dir, "output.jar")
            compile_cmd = f"kotlinc {kotlin_file} -include-runtime -d {jar_file}"

            compile_result = subprocess.run(
                compile_cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"Kotlin compilation failed: {compile_result.stderr}")

            # Execute Kotlin code
            cmd = f"java -jar {jar_file}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"Kotlin execution failed: {run_result.stderr}")

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
            if kotlin_file and os.path.exists(kotlin_file) and 'file' not in self._params:
                os.unlink(kotlin_file)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self