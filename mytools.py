from contextlib import contextmanager
import os
import subprocess

@contextmanager
def cwd(path):
    oldpwd=os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def capture2(cmd, shell = False):
    os.environ['PYTHONUNBUFFERED'] = "1"
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            shell = shell,
                            universal_newlines = True,
                            )
    stdout, stderr = proc.communicate()

    return proc.returncode, stdout
