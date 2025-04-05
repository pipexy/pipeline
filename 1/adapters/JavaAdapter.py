"""
JavaAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class JavaAdapter(ChainableAdapter):
    """Adapter for executing Java code."""

    def _execute_self(self, input_data=None):
        # Create temporary files
        java_file = None
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

            # Get the Java code from params
            code = self._params.get('code')
            class_name = self._params.get('class_name', 'TempJavaClass')

            if not code:
                raise ValueError("Java adapter requires 'code' method")

            # Create a temporary Java file
            with tempfile.NamedTemporaryFile(suffix=".java", delete=False, mode='w+') as f:
                # If code doesn't include class definition, wrap it in a class
                if f"class {class_name}" not in code:
                    wrapped_code = f"""
                    import java.util.*;
                    import java.io.*;
                    import java.nio.file.*;

                    public class {class_name} {{
                        public static void main(String[] args) throws Exception {{
                            String inputPath = args.length > 0 ? args[0] : null;
                            String input = null;
                            
                            if (inputPath != null) {{
                                input = new String(Files.readAllBytes(Paths.get(inputPath)));
                            }}
                            
                            {code}
                        }}
                    }}
                    """
                    f.write(wrapped_code)
                else:
                    f.write(code)

                java_file = f.name

            # Compile the Java code
            compile_result = subprocess.run(
                f"javac {java_file}",
                shell=True,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"Java compilation failed: {compile_result.stderr}")

            # Run the Java code
            cmd = f"java -cp {os.path.dirname(java_file)} {class_name}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
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
            if java_file and os.path.exists(java_file):
                os.unlink(java_file)
                # Remove .class file
                class_file = java_file.replace('.java', '.class')
                if os.path.exists(class_file):
                    os.unlink(class_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self