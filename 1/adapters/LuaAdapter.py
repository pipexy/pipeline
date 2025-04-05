"""
LuaAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class LuaAdapter(ChainableAdapter):
    """Adapter for executing Lua code."""

    def code(self, lua_code):
        """Set Lua code to execute."""
        self._params['code'] = lua_code
        return self

    def script(self, script_path):
        """Set Lua script path to execute."""
        self._params['script'] = script_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        lua_file = None
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

            # Get the Lua code/script
            code = self._params.get('code')
            script = self._params.get('script')

            if not code and not script:
                raise ValueError("Lua adapter requires either 'code' or 'script' parameter")

            if code:
                # Create a Lua file with wrapper for input handling
                with tempfile.NamedTemporaryFile(suffix=".lua", delete=False, mode='w+') as f:
                    wrapper_code = """
                    -- JSON helper function
                    function parseJson(str)
                        -- Simple JSON parsing for basic types
                        local function trim(s)
                            return s:match("^%s*(.-)%s*$")
                        end

                        str = trim(str)

                        if str:sub(1,1) == '{' and str:sub(-1) == '}' then
                            -- Parse as object/table
                            local result = {}
                            -- Very simple parsing, won't handle complex JSON
                            for k, v in str:gmatch('"([^"]+)"%s*:%s*"?([^",{}%[%]]+)"?,?') do
                                result[k] = v
                            end
                            return result
                        elseif str:sub(1,1) == '[' and str:sub(-1) == ']' then
                            -- Parse as array
                            local result = {}
                            -- Very simple parsing, won't handle complex JSON
                            for v in str:gmatch('"?([^",{}%[%]]+)"?,?') do
                                table.insert(result, v)
                            end
                            return result
                        else
                            -- Return as is
                            return str
                        end
                    end

                    -- Parse input if available
                    local input_data = nil
                    if arg and arg[1] then
                        local input_path = arg[1]
                        local file = io.open(input_path, "r")
                        if file then
                            local content = file:read("*all")
                            file:close()
                            -- Try to parse as JSON (simplified)
                            input_data = parseJson(content)
                        end
                    end

                    -- User code starts here
                    %s
                    """
                    f.write(wrapper_code % code)
                    lua_file = f.name
            else:
                # Use the provided script path
                lua_file = script

            # Execute Lua file
            cmd = f"lua {lua_file}"
            if input_file:
                cmd += f" {input_file}"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Lua execution failed: {result.stderr}")

            # Return the output
            output = result.stdout.strip()

            # Try parsing as JSON if it looks like JSON
            if output.startswith('{') or output.startswith('['):
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    pass

            return output

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Lua execution error: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Lua adapter error: {str(e)}")
        finally:
            # Clean up temporary files
            if lua_file and os.path.exists(lua_file) and 'script' not in self._params:
                os.unlink(lua_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self