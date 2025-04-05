"""
JavaAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class JavaAdapter(ChainableAdapter):
    """Adapter for compiling and executing Java code."""

    def code(self, java_code):
        """Set Java code to execute."""
        self._params['code'] = java_code
        return self

    def file(self, file_path):
        """Set Java file to execute."""
        self._params['file'] = file_path
        return self

    def class_name(self, name):
        """Set Java class name."""
        self._params['class_name'] = name
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        java_file = None
        input_file = None
        temp_dir = None

        try:
            # Create temp directory for compilation
            temp_dir = tempfile.mkdtemp()

            # Handle input data
            if input_data:
                with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                    if isinstance(input_data, (dict, list)):
                        json.dump(input_data, f)
                    else:
                        f.write(str(input_data))
                    input_file = f.name

            # Get the Java code or file
            code = self._params.get('code')
            file_path = self._params.get('file')

            if not code and not file_path:
                raise ValueError("Java adapter requires either 'code' or 'file' parameter")

            # Determine class name
            class_name = self._params.get('class_name', 'Main')

            if code:
                # Create a Java file with input handling wrapper
                java_file = os.path.join(temp_dir, f"{class_name}.java")

                wrapper_code = """
                import java.io.*;
                import java.nio.file.*;
                import org.json.*;

                public class %s {
                    // Function to read input data
                    private static String readInput(String[] args) {
                        if (args.length > 0) {
                            try {
                                return new String(Files.readAllBytes(Paths.get(args[0])));
                            } catch (Exception e) {
                                System.err.println("Error reading input file: " + e.getMessage());
                            }
                        }
                        return null;
                    }

                    %s
                }
                """

                # Remove any existing class declaration
                user_code = code.replace("public class " + class_name, "")
                user_code = user_code.replace("class " + class_name, "")

                with open(java_file, 'w') as f:
                    f.write(wrapper_code % (class_name, user_code))
            else:
                # Copy the file to temp dir to avoid classpath issues
                java_file = os.path.join(temp_dir, os.path.basename(file_path))
                with open(file_path, 'r') as src, open(java_file, 'w') as dst:
                    dst.write(src.read())

            # Compile Java code
            compile_cmd = f"javac {java_file}"
            compile_result = subprocess.run(
                compile_cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=temp_dir
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"Java compilation failed: {compile_result.stderr}")

            # Execute Java code
            cmd = f"java -cp {temp_dir} {class_name}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=temp_dir
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"Java execution failed: {run_result.stderr}")

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
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self