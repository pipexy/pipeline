"""
SwiftAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class SwiftAdapter(ChainableAdapter):
    """Adapter for executing Swift code."""

    def code(self, swift_code):
        """Set Swift code to execute."""
        self._params['code'] = swift_code
        return self

    def script(self, script_path):
        """Set Swift script path to execute."""
        self._params['script'] = script_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        swift_file = None
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

            # Get the Swift code/script
            code = self._params.get('code')
            script = self._params.get('script')

            if not code and not script:
                raise ValueError("Swift adapter requires either 'code' or 'script' parameter")

            if code:
                # Create a Swift file with a wrapper for input handling
                with tempfile.NamedTemporaryFile(suffix=".swift", delete=False, mode='w+') as f:
                    wrapper_code = """
                    import Foundation

                    // Parse input if available
                    var inputData: Any? = nil
                    if CommandLine.arguments.count > 1 {
                        let inputPath = CommandLine.arguments[1]
                        if let data = try? Data(contentsOf: URL(fileURLWithPath: inputPath)) {
                            let content = String(data: data, encoding: .utf8)
                            
                            // Try to parse as JSON
                            if let jsonData = content?.data(using: .utf8) {
                                do {
                                    inputData = try JSONSerialization.jsonObject(with: jsonData, options: [])
                                } catch {
                                    // If not valid JSON, use as string
                                    inputData = content
                                }
                            }
                        }
                    }

                    // User code starts here
                    %s
                    """
                    f.write(wrapper_code % code)
                    swift_file = f.name
            else:
                # Use the provided script path
                swift_file = script

            # Execute Swift file
            cmd = f"swift {swift_file}"
            if input_file:
                cmd += f" {input_file}"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Swift execution failed: {result.stderr}")

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
            raise RuntimeError(f"Swift execution error: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Swift adapter error: {str(e)}")
        finally:
            # Clean up temporary files
            if swift_file and os.path.exists(swift_file) and 'script' not in self._params:
                os.unlink(swift_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self