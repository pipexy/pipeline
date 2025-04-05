"""
CppAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class CppAdapter(ChainableAdapter):
    """Adapter for compiling and executing C++ code."""

    def code(self, cpp_code):
        """Set C++ code to execute."""
        self._params['code'] = cpp_code
        return self

    def file(self, file_path):
        """Set C++ file to compile and execute."""
        self._params['file'] = file_path
        return self

    def compiler_flags(self, flags):
        """Set compiler flags."""
        self._params['compiler_flags'] = flags
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        cpp_file = None
        input_file = None
        exe_file = None

        try:
            # Handle input data
            if input_data:
                with tempfile.NamedTemporaryFile(delete=False, mode='w+') as f:
                    if isinstance(input_data, (dict, list)):
                        json.dump(input_data, f)
                    else:
                        f.write(str(input_data))
                    input_file = f.name

            # Get the C++ code or file
            code = self._params.get('code')
            file_path = self._params.get('file')
            compiler_flags = self._params.get('compiler_flags', '-std=c++17')

            if not code and not file_path:
                raise ValueError("C++ adapter requires either 'code' or 'file' parameter")

            if code:
                # Create a C++ file with input handling wrapper
                with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False, mode='w+') as f:
                    wrapper_code = """
                    #include <iostream>
                    #include <fstream>
                    #include <string>
                    #include <sstream>
                    #include <vector>
                    
                    // Simple JSON helper functions
                    namespace json {
                        std::string get_string(const std::string& json, const std::string& key) {
                            // Simple extraction, not full JSON parsing
                            size_t pos = json.find("\"" + key + "\"");
                            if (pos == std::string::npos) return "";
                            pos = json.find(":", pos);
                            if (pos == std::string::npos) return "";
                            pos = json.find("\"", pos);
                            if (pos == std::string::npos) return "";
                            size_t end = json.find("\"", pos + 1);
                            if (end == std::string::npos) return "";
                            return json.substr(pos + 1, end - pos - 1);
                        }
                    }

                    int main(int argc, char* argv[]) {
                        std::string input_data;
                        
                        // Read input file if provided
                        if (argc > 1) {
                            std::ifstream input_file(argv[1]);
                            if (input_file.is_open()) {
                                std::stringstream buffer;
                                buffer << input_file.rdbuf();
                                input_data = buffer.str();
                            }
                        }
                        
                        // User code starts here
                        %s
                        
                        return 0;
                    }
                    """
                    f.write(wrapper_code % code)
                    cpp_file = f.name
            else:
                # Use the provided file
                cpp_file = file_path

            # Create temp executable file
            exe_file = f"{cpp_file}.out"

            # Compile the C++ code
            compile_cmd = f"g++ {cpp_file} -o {exe_file} {compiler_flags}"
            compile_result = subprocess.run(
                compile_cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"C++ compilation failed: {compile_result.stderr}")

            # Make executable
            os.chmod(exe_file, 0o755)

            # Execute the compiled program
            cmd = f"{exe_file}"
            if input_file:
                cmd += f" {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"C++ execution failed: {run_result.stderr}")

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
            if cpp_file and os.path.exists(cpp_file) and 'file' not in self._params:
                os.unlink(cpp_file)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)
            if exe_file and os.path.exists(exe_file):
                os.unlink(exe_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self