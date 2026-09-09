import subprocess


class TerminalClient:
    def __init__(self, working_directory: str):
        self.working_directory = working_directory

    def execute(self, command: str):
        result = subprocess.run(
            command,
            shell=True,
            cwd=self.working_directory,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }