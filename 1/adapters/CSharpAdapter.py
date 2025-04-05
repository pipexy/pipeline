"""
CSharpAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class CSharpAdapter(ChainableAdapter):
    """Adapter for executing C# code."""

    def _execute_self(self, input_data=None):
        # Create temporary files
        cs_file = None
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

            # Get the C# code
            code = self._params.get('code')
            if not code:
                raise ValueError("CSharp adapter requires 'code' method")

            # Create a C# file
            with tempfile.NamedTemporaryFile(suffix=".cs", delete=False, mode='w+') as f:
                # If no class definition, wrap in a Program class
                if "class Program" not in code:
                    wrapped_code = """
                    using System;
                    using System.IO;
                    using System.Text.Json;

                    class Program
                    {
                        static void Main(string[] args)
                        {
                            object input = null;
                            
                            if (args.Length > 0)
                            {
                                try
                                {
                                    string content = File.ReadAllText(args[0]);
                                    try
                                    {
                                        input = JsonSerializer.Deserialize<object>(content);
                                    }
                                    catch
                                    {
                                        input = content;
                                    }
                                }
                                catch (Exception ex)
                                {
                                    Console.Error.WriteLine($"Error reading input file: {ex.Message}");
                                }
                            }
                            
                            // User code starts here
                            %s
                        }
                    }
                    """
                    f.write(wrapped_code % code)
                else:
                    f.write(code)

                cs_file = f.name

            # Compile the C# code
            compiled_file = f"{cs_file}.exe"
            compile_cmd = f"csc {cs_file} -out:{compiled_file}"

            compile_result = subprocess.run(
                compile_cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"C# compilation failed: {compile_result.stderr}")

            # Execute the compiled C# program
            exec_cmd = f"mono {compiled_file}"
            if input_file:
                exec_cmd += f" {input_file}"

            result = subprocess.run(
                exec_cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"C# execution failed: {result.stderr}")

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
            if cs_file and os.path.exists(cs_file):
                os.unlink(cs_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

            if compiled_file and os.path.exists(compiled_file):
                os.unlink(compiled_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self