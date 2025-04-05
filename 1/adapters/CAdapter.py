"""
CAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class CAdapter(ChainableAdapter):
    """Adapter for compiling and executing C code."""

    def code(self, c_code):
        """Set C code to execute."""
        self._params['code'] = c_code
        return self

    def file(self, file_path):
        """Set C file to compile and execute."""
        self._params['file'] = file_path
        return self

    def compiler_flags(self, flags):
        """Set compiler flags."""
        self._params['compiler_flags'] = flags
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        c_file = None
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

            # Get the C code or file
            code = self._params.get('code')
            file_path = self._params.get('file')
            compiler_flags = self._params.get('compiler_flags', '')

            if not code and not file_path:
                raise ValueError("C adapter requires either 'code' or 'file' parameter")

            if code:
                # Create a C file with input handling wrapper
                with tempfile.NamedTemporaryFile(suffix=".c", delete=False, mode='w+') as f:
                    wrapper_code = """
                    #include <stdio.h>
                    #include <stdlib.h>
                    #include <string.h>

                    // Simple JSON parsing function for demonstration
                    // In real use, you'd want a proper JSON library
                    char* get_str_value(const char* json, const char* key) {
                        char search_key[256];
                        sprintf(search_key, "\"%s\":", key);
                        
                        char* key_pos = strstr(json, search_key);
                        if(!key_pos) return NULL;
                        
                        key_pos += strlen(search_key);
                        while(*key_pos == ' ' || *key_pos == '\\t') key_pos++;
                        
                        if(*key_pos == '"') {
                            key_pos++;
                            char* end = strchr(key_pos, '"');
                            if(!end) return NULL;
                            
                            int len = end - key_pos;
                            char* result = malloc(len + 1);
                            strncpy(result, key_pos, len);
                            result[len] = '\\0';
                            return result;
                        }
                        return NULL;
                    }

                    int main(int argc, char *argv[]) {
                        FILE *file = NULL;
                        char *input = NULL;
                        long file_size = 0;
                        
                        if(argc > 1) {
                            file = fopen(argv[1], "r");
                            if(file) {
                                fseek(file, 0, SEEK_END);
                                file_size = ftell(file);
                                rewind(file);
                                
                                input = malloc(file_size + 1);
                                if(input) {
                                    fread(input, 1, file_size, file);
                                    input[file_size] = '\\0';
                                }
                                fclose(file);
                            }
                        }
                        
                        // User code starts here
                        %s
                        
                        // Clean up
                        if(input) free(input);
                        return 0;
                    }
                    """
                    f.write(wrapper_code % code)
                    c_file = f.name
            else:
                # Use the provided file
                c_file = file_path

            # Create temp executable file
            exe_file = f"{c_file}.out"

            # Compile the C code
            compile_cmd = f"gcc {c_file} -o {exe_file} {compiler_flags}"
            compile_result = subprocess.run(
                compile_cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"C compilation failed: {compile_result.stderr}")

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
                raise RuntimeError(f"C execution failed: {run_result.stderr}")

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
            if c_file and os.path.exists(c_file) and 'file' not in self._params:
                os.unlink(c_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

            if exe_file and os.path.exists(exe_file):
                os.unlink(exe_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self