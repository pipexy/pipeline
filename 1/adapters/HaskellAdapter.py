"""
HaskellAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class HaskellAdapter(ChainableAdapter):
    """Adapter for compiling and executing Haskell code."""

    def code(self, haskell_code):
        """Set Haskell code to execute."""
        self._params['code'] = haskell_code
        return self

    def file(self, file_path):
        """Set Haskell file to execute."""
        self._params['file'] = file_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        haskell_file = None
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

            # Get the Haskell code or file
            code = self._params.get('code')
            file_path = self._params.get('file')

            if not code and not file_path:
                raise ValueError("Haskell adapter requires either 'code' or 'file' parameter")

            if code:
                # Create a Haskell file with input handling wrapper
                with tempfile.NamedTemporaryFile(suffix=".hs", delete=False, mode='w+') as f:
                    wrapper_code = """
                    import System.Environment
                    import System.IO
                    import qualified Data.ByteString.Lazy as B
                    import qualified Data.Aeson as Aeson
                    import Data.Maybe (fromMaybe)

                    -- Function to read input data
                    readInputData :: IO (Maybe String)
                    readInputData = do
                        args <- getArgs
                        case args of
                            (inputFile:_) -> do
                                content <- readFile inputFile
                                return $ Just content
                            _ -> return Nothing

                    -- User code starts here
                    %s

                    -- Main function
                    main :: IO ()
                    main = do
                        inputMaybe <- readInputData
                        -- Your code can handle input in the functions above
                    """
                    f.write(wrapper_code % code)
                    haskell_file = f.name
            else:
                # Use the provided file
                haskell_file = file_path

            # Create output file name
            temp_dir = tempfile.mkdtemp()
            exe_file = os.path.join(temp_dir, "haskell_program")

            # Compile the Haskell code
            compile_cmd = f"ghc -o {exe_file} {haskell_file}"
            compile_result = subprocess.run(
                compile_cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise RuntimeError(f"Haskell compilation failed: {compile_result.stderr}")

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
                raise RuntimeError(f"Haskell execution failed: {run_result.stderr}")

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
            if haskell_file and os.path.exists(haskell_file) and 'file' not in self._params:
                os.unlink(haskell_file)
            if input_file and os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self