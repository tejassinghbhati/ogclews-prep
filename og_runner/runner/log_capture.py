# runner/log_capture.py
import sys
import logging
from pathlib import Path

class TeeStream:
    """Writes to both a file and the original stream."""
    def __init__(self, file_path: Path, original_stream):
        self.file = open(file_path, "w", buffering=1)  # line-buffered
        self.original = original_stream

    def write(self, data):
        self.file.write(data)
        self.original.write(data)

    def flush(self):
        self.file.flush()
        self.original.flush()

    def close(self):
        self.file.close()

class LogCapture:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._stdout_tee = None
        self._stderr_tee = None
        self._orig_stdout = None
        self._orig_stderr = None

    def __enter__(self):
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        self._stdout_tee = TeeStream(self.log_path, self._orig_stdout)
        self._stderr_tee = TeeStream(self.log_path, self._orig_stderr)
        sys.stdout = self._stdout_tee
        sys.stderr = self._stderr_tee
        return self

    def __exit__(self, *args):
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr
        self._stdout_tee.close()
        self._stderr_tee.close()