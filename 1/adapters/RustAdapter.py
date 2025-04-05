"""
RustAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class RustAdapter(ChainableAdapter):
    """Adapter for compiling and executing Rust code."""

    def code(self, rust_code):
        """Set Rust code to execute."""
        self._params['code'] = rust_code
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        rust_file = None
        cargo_dir = None
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

            # Get Rust code
            code = self._params.get('code')
            if not code:
                raise ValueError("Rust adapter requires 'code' parameter")

            # Create a temporary Cargo project
            cargo_dir = tempfile.mkdtemp()

            # Initialize Cargo project
            subprocess.run(
                f"cargo init --bin {cargo_dir}",
                shell=True,
                capture_output=True,
                check=True
            )

            # Write Rust code to main.rs
            rust_file = os.path.join(cargo_dir, "src", "main.rs")

            # Prepare the Rust code with input handling
            if "fn main()" not in code:
                full_code = """
                use std::env;
                use std::fs;
                use std::path::Path;
                use serde_json;

                fn main() {
                    let args: Vec<String> = env::args().collect();
                    let mut input_data = None;
                    
                    if args.len() > 1 {
                        let input_path = &args[1];
                        if Path::new(input_path).exists() {
                            let content = fs::read_to_string(input_path).expect("Failed to read input file");
                            
                            // Try to parse as JSON
                            input_data = match serde_json::from_str(&content) {
                                Ok(json) => Some(json),
                                Err(_) => Some(content)
                            };
                        }
                    }
                    
                    // User code starts here
                    %s
                }
                """
                code_to_write = full_code % code
            else:
                code_to_write = code

            with open(rust_file, 'w') as f:
                f.write(code_to_write)

            # Add serde dependencies for JSON handling
            cargo_toml = os.path.join(cargo_dir, "Cargo.toml")
            with open(cargo_toml, 'a') as f:
                f.write("\n[dependencies]\nserde = { version = \"1.0\", features = [\"derive\"] }\nserde_json = \"1.0\"\n")

            # Build the Rust project
            build_result = subprocess.run(
                f"cd {cargo_dir} && cargo build --quiet",
                shell=True,
                capture_output=True,
                text=True
            )

            if build_result.returncode != 0:
                raise RuntimeError(f"Rust compilation failed:\n{build_result.stderr}")

            # Run the Rust binary
            cmd = f"cd {cargo_dir} && cargo run --quiet"
            if input_file:
                cmd += f" -- {input_file}"

            run_result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if run_result.returncode != 0:
                raise RuntimeError(f"Rust execution failed:\n{run_result.stderr}")

            # Return the output
            output = run_result.stdout.strip()

            # Try parsing as JSON if it looks like JSON
            if output.startswith('{') or output.startswith('['):
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    pass

            return output

        except Exception as e:
            raise RuntimeError(f"Rust adapter error: {str(e)}")

        finally:
            # Clean up temporary files and directories
            import shutil
            if cargo_dir and os.path.exists(cargo_dir):
                shutil.rmtree(cargo_dir)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self