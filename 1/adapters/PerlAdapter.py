"""
PerlAdapter.py
"""
import subprocess
import tempfile
import os
import json
from .ChainableAdapter import ChainableAdapter


class PerlAdapter(ChainableAdapter):
    """Adapter for executing Perl code."""

    def code(self, perl_code):
        """Set Perl code to execute."""
        self._params['code'] = perl_code
        return self

    def script(self, script_path):
        """Set Perl script path to execute."""
        self._params['script'] = script_path
        return self

    def _execute_self(self, input_data=None):
        # Create temporary files
        perl_file = None
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

            # Get the Perl code/script
            code = self._params.get('code')
            script = self._params.get('script')

            if not code and not script:
                raise ValueError("Perl adapter requires either 'code' or 'script' parameter")

            if code:
                # Create a Perl file
                with tempfile.NamedTemporaryFile(suffix=".pl", delete=False, mode='w+') as f:
                    # Wrapper to handle input
                    wrapper_code = """
                    use strict;
                    use warnings;
                    use JSON;

                    my $input_data = undef;

                    if (@ARGV) {
                        my $input_file = $ARGV[0];
                        if (open my $fh, '<', $input_file) {
                            local $/;
                            my $content = <$fh>;
                            close $fh;
                            
                            # Try to parse as JSON
                            eval {
                                $input_data = decode_json($content);
                            };
                            if ($@) {
                                # Not valid JSON, use as string
                                $input_data = $content;
                            }
                        }
                    }

                    # User code starts here
                    %s
                    """
                    f.write(wrapper_code % code)
                    perl_file = f.name
            else:
                # Use the provided script path
                perl_file = script

            # Execute Perl file
            cmd = f"perl {perl_file}"
            if input_file:
                cmd += f" {input_file}"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Perl execution failed: {result.stderr}")

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
            if perl_file and os.path.exists(perl_file) and 'script' not in self._params:
                os.unlink(perl_file)

            if input_file and os.path.exists(input_file):
                os.unlink(input_file)

    def reset(self):
        """Resets adapter parameters."""
        self._params = {}
        return self