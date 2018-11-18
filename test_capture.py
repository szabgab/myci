import subprocess
from mytools import capture2

def test_capture():
    cmd = ['git', '--no-pager', 'show', '-s', "--format=%an", '1548a62d2db12b9b2afcd996aac015d3c373bae8']
    author_name  = subprocess.check_output(cmd)
    assert author_name == b'Gabor Szabo\n'
    
    code, auth_name = capture2(cmd)
    assert code == 0
    assert auth_name == 'Gabor Szabo\n'

