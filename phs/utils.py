import sys
import shutil


RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def set_default_value_to_optional_key(key, value, dict):
    if key not in dict:
        dict[key] = value
    return dict[key]


def print_section(header):
    """
    Print a green section header formated with '=' filling up the complete terminal width.
    If terminal width cannot be If the terminal size cannot be successfully queried,
    either because the system doesn’t support querying, or because we are not connected to a terminal,
    the default value is (80, 24) which is the default size used by many terminal emulators.
    """
    terminal_cols, _ = shutil.get_terminal_size()
    sys.stdout.write(GREEN)
    print('{:=^{width}}' .format('', width=terminal_cols))
    print('{:=^{width}}' .format(' ' + header + ' ', width=terminal_cols))
    print('{:=^{width}}' .format('', width=terminal_cols))
    sys.stdout.write(RESET)


def print_subsection(header):
    """
    Print a green section header formated with '-' filling up the complete terminal width.
    If terminal width cannot be If the terminal size cannot be successfully queried,
    either because the system doesn’t support querying, or because we are not connected to a terminal,
    the default value is (80, 24) which is the default size used by many terminal emulators.
    """
    terminal_cols, _ = shutil.get_terminal_size()
    sys.stdout.write(GREEN)
    print('{:-^{width}}' .format('', width=terminal_cols))
    print('{:-^{width}}' .format(' ' + header + ' ', width=terminal_cols))
    print('{:-^{width}}' .format('', width=terminal_cols))
    sys.stdout.write(RESET)


def format_stderr():
    sys.stderr.write(RED)


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


def comp_files_and_dirs(dcmp, result=None):
    if result is None:
        result = []
    for name in dcmp.diff_files:
        result.append("diff_file %s found in %s and %s" % (name, dcmp.left, dcmp.right))
    for name in dcmp.left_only:
        result.append("file/dir %s found only in %s" % (name, dcmp.left))
    for name in dcmp.right_only:
        result.append("file/dir %s found only in %s" % (name, dcmp.right))
    for sub_dcmp in dcmp.subdirs.values():
        comp_files_and_dirs(sub_dcmp, result)
    return result
