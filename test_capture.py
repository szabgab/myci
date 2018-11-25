import subprocess
import sys
from myci.tools import capture2

def test_capture():
    cmd = ['git', '--no-pager', 'show', '-s', "--format=%an", '1548a62d2db12b9b2afcd996aac015d3c373bae8']
    author_name  = subprocess.check_output(cmd)
    assert author_name == b'Gabor Szabo\n'

    code, auth_name = capture2(cmd)
    assert code == 0
    assert auth_name == 'Gabor Szabo\n'

    code, output = capture2([sys.executable, "test/exceptional.py"])
    assert code == 1
    assert output == "Parameters are 'raise', 'good', N\n"

    code, output = capture2([sys.executable, "test/exceptional.py", 'over'])
    assert code == 1
    print(output)
    assert 'Traceback (most recent call last):' in output
    assert 'IndexError: list index out of range' in output

    code, output = capture2([sys.executable, "test/exceptional.py", "42"])
    assert code == 42
    assert output == ''


    code, output = capture2([sys.executable, "test/exceptional.py", "raise"])
    assert code == 1
    assert 'Traceback (most recent call last):' in output
    assert 'Exception: Something bad happened.' in output
