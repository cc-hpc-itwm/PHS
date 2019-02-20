import sys

def set_default_value_to_optional_key(key, value, dict):
    if key not in dict:
        dict[key] = value
    return dict[key]


def print_section(header):
    print('{:=^120}' .format(''))
    print('{:=^120}' .format(' ' + header + ' '))
    print('{:=^120}' .format(''))


def print_subsection(header):
    print('{:-^120}' .format(''))
    print('{:-^120}' .format(' ' + header + ' '))
    print('{:-^120}' .format(''))


class RedirectStdoutStream:
    def __init__(self, stdout_file):
        self.stdout_file = stdout_file


    def __enter__(self):
        self.stdout_handle = open(self.stdout_file, 'w')
        self.original_stdout = sys.stdout
        self.original_stdout.flush()
        sys.stdout = self.stdout_handle
        
    def __exit__(self, *args):
        self.stdout_handle.flush()
        sys.stdout = self.original_stdout
        self.stdout_handle.close()

# not working
class RedirectStderrStream:
    def __init__(self, stderr_file):
        self.stderr_file = stderr_file

    def __enter__(self):
        self.stderr_handle = open(self.stderr_file, 'w')
        self.original_stderr = sys.stderr
        self.original_stderr.flush()
        sys.stderr = self.stderr_handle

    def __exit__(self, *args):
        self.stderr_handle.flush()
        sys.stderr = self.original_stderr
        self.stderr_handle.close()