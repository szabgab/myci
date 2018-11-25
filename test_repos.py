from myci.tools import cwd, capture2
import json
import os
import yaml

debug = ''
if os.environ.get('DEBUG'):
    debug = '--debug'


def _system(cmd):
    print(cmd)
    os.system(cmd)

class TestRepo(object):
    def test_repo(self, tmpdir):
        temp_dir = str(tmpdir)
        print(temp_dir)
        self.setup_repos(temp_dir, {}, 1)

        _system("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug))
        assert os.path.exists( os.path.join(self.repositories, 'repo0') )
        assert os.listdir( os.path.join(self.repositories, 'repo0/') ) == ['.git']
        assert not os.path.exists(os.path.join(self.workdir, '1', 'repo0/'))

        # update the repository
        with cwd(self.client[0]):
            with open('README.txt', 'w') as fh:
                fh.write("first line\n")
            _system("git add .")
            _system("git commit -m 'first' --author 'Foo Bar <foo@bar.com>'")
            _system("git push")
        _system("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug))
        assert os.listdir( os.path.join(self.repositories, 'repo0/') ) == ['README.txt', '.git']
        assert os.path.exists(os.path.join(self.workdir, '1', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '1', 'repo0/')) == ['README.txt', '.git']
        # check if the sha change was noticed git rev-parse HEAD

        # create a branch, see if the new branch is noticed
        with cwd(self.client[0]):
            with open('TODO', 'w') as fh:
                fh.write("Some TODO text\n")
            _system("git checkout -b todo")
            _system("git add .")
            _system("git commit -m 'add test' --author 'Foo Bar <foo@bar.com>'")
            _system("git push --set-upstream origin todo")

            _system("git checkout master")
            with open('MASTER', 'w') as fh:
                fh.write("Some MASTER text\n")
            _system("git add .")
            _system("git commit -m 'add master' --author 'Foo Bar <foo@bar.com>'")
            _system("git push")
        code, out = capture2("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug), shell=True)
        print(out)
        assert code == 0

        # first workdir did not change
        assert os.path.exists(os.path.join(self.workdir, '1', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '1', 'repo0/')) == ['README.txt', '.git']

        # second workdir has the new file as well
        assert os.path.exists(os.path.join(self.workdir, '2', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '2', 'repo0/')) == ['MASTER', 'README.txt', '.git']

        # second workdir has the new file as well
        assert os.path.exists(os.path.join(self.workdir, '3', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '3', 'repo0/')) == ['TODO', 'README.txt', '.git']

    def test_run_tests(self, tmpdir):
        temp_dir = str(tmpdir)
        print(temp_dir)
        self.setup_repos(temp_dir, {
            'steps': [
                "cli: python repo0/selftest.py"
            ]
        }, 1)

        # update the repository
        with cwd(self.client[0]):
            with open('selftest.py', 'w') as fh:
                fh.write("exit(13)\n")
            _system("git add .")
            _system("git commit -m 'first' --author 'Foo Bar <foo@bar.com>'")
            _system("git push")
        code, out = capture2("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug), shell=True)
        print(out)
        assert code == 1, "One test failure repored"
        #assert out == "" # TODO: this will fail if --debug is on, but also becaues there is some output from the git commands.
        assert os.listdir( os.path.join(self.repositories, 'repo0/') ) == ['selftest.py', '.git']
        assert os.path.exists(os.path.join(self.workdir, '1', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '1', 'repo0/')) == ['selftest.py', '.git']


        with cwd(self.client[0]):
            with open('selftest.py', 'w') as fh:
                fh.write("exit(0)\n")
            _system("git add .")
            _system("git commit -m 'second' --author 'Foo Bar <foo@bar.com>'")
            _system("git push")
        code, out = capture2("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug), shell=True)
        print(out)
        assert code == 0, "test sucess repored: "
        #assert out == "" # TODO: this will fail if --debug is on, but also becaues there is some output from the git commands.
        assert os.listdir( os.path.join(self.repositories, 'repo0/') ) == ['selftest.py', '.git']
        assert os.path.exists(os.path.join(self.workdir, '2', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '2', 'repo0/')) == ['selftest.py', '.git']

    def test_run_matrix(self, tmpdir):
        temp_dir = str(tmpdir)
        print(temp_dir)
        self.setup_repos(temp_dir, {
            'matrix': [
                    {
                        'agent': 'master',
                        'exe': 'python repo0/code.py Foo',
                    },
                    {
                        'agent': 'master',
                        'exe': 'python repo0/code.py',
                    },
                    {
                        'agent': 'master',
                        'exe': 'python repo0/code.py Bar',
                    },
                    {
                        'agent': 'master',
                        'exe': 'python repo0/code.py crash',
                    },
            ]
        }, 1)

        # update the repository
        with cwd(self.client[0]):
            with open('code.py', 'w') as fh:
                fh.write("""
import sys
if len(sys.argv) < 2:
    exit("Missing parameter")
print("hello " + sys.argv[1])
if sys.argv[1] == "crash":
    v = 0
    print(42/v)
""")

            _system("git add .")
            _system("git commit -m 'first' --author 'Foo Bar <foo@bar.com>'")
            _system("git push")
        code, out = capture2("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug), shell=True)
        print(out)
        assert code == 1, "some tests failed in the matrix"
        #assert out == "" # TODO: this will fail if --debug is on, but also becaues there is some output from the git commands.
        assert os.listdir( os.path.join(self.repositories, 'repo0/') ) == ['code.py', '.git']
        assert os.path.exists(os.path.join(self.workdir, '1/1', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '1/1', 'repo0/')) == ['code.py', '.git']
        assert os.path.exists(os.path.join(self.workdir, '1/2', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '1/2', 'repo0/')) == ['code.py', '.git']
        results_file = os.path.join(self.db, '1.json')
        assert os.path.exists( results_file )
        with open(results_file) as fh:
            results = json.load(fh)
        last = results['matrix'].pop('4')
        assert results == {
            'status': 'failure',
            'matrix': {
                '1': {'exit': 0, 'agent': 'master', 'exe': 'python repo0/code.py Foo', 'out': 'hello Foo\n'},
                '2': {'exit': 1, 'agent': 'master', 'exe': 'python repo0/code.py', 'out': 'Missing parameter\n'},
                '3': {'exit': 0, 'agent': 'master', 'exe': 'python repo0/code.py Bar', 'out': 'hello Bar\n'},
            },
        }
        out_of_last = last.pop('out')
        assert last == {
            'exit': 1,
            'agent': 'master',
            'exe': 'python repo0/code.py crash',
        }
        # Then end of the error message has changed so we don't test the specifics
        # In Python 2: integer division or modulo by zero
        # In Python 3: division by zero
        assert 'hello crash\nTraceback (most recent call last):\n  File "repo0/code.py", line 8, in <module>\n    print(42/v)\nZeroDivisionError:' in out_of_last

    def test_repos(self, tmpdir):
        temp_dir = str(tmpdir)
        print(temp_dir)
        self.setup_repos(temp_dir, {}, 2)

        _system("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug))
        assert os.path.exists( os.path.join(self.repositories, 'repo0') )
        assert os.listdir( os.path.join(self.repositories, 'repo0/') ) == ['.git']
        assert not os.path.exists(os.path.join(self.workdir, '1', 'repo0/'))

        assert os.path.exists( os.path.join(self.repositories, 'repo1') )
        assert os.listdir( os.path.join(self.repositories, 'repo1/') ) == ['.git']
        assert not os.path.exists(os.path.join(self.workdir, '1', 'repo1/'))

        # update the repository
        with cwd(self.client[0]):
            with open('README.txt', 'w') as fh:
                fh.write("first line\n")
            _system("git add .")
            _system("git commit -m 'first' --author 'Foo Bar <foo@bar.com>'")
            _system("git push")

        with cwd(self.client[1]):
            with open('selftest.py', 'w') as fh:
                fh.write("assert True\n")
            _system("git add .")
            _system("git commit -m 'start with test' --author 'Zee No <zee@no.com>'")
            _system("git push")

        _system("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug))
        assert os.listdir( os.path.join(self.repositories, 'repo0/') ) == ['README.txt', '.git']
        assert os.path.exists(os.path.join(self.workdir, '1', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '1', 'repo0/')) == ['README.txt', '.git']

        assert os.listdir( os.path.join(self.repositories, 'repo1/') ) == ['selftest.py', '.git']
        assert os.path.exists(os.path.join(self.workdir, '1', 'repo1/'))
        assert os.listdir(os.path.join(self.workdir, '1', 'repo1/')) == ['selftest.py', '.git']

        # results_file = os.path.join(self.db, '1.json')
        # assert os.path.exists( results_file )
        # with open(results_file) as fh:
        #     results = json.load(fh)
        #     #print(results)

        # check if the sha change was noticed git rev-parse HEAD



    def setup_repos(self, temp_dir, user_config, count):
        remote_repos = os.path.join(temp_dir, 'remote_repos')  # bare repos
        client_dir = os.path.join(temp_dir, 'client')  # workspace of users
        root = os.path.join(temp_dir, 'server')
        self.server_file = os.path.join(root, 'server.yml')
        self.config_file = os.path.join(root, 'config.yml')  # this might be in a repository
        self.repositories = os.path.join(root, 'repositories')  # here is where we'll clone repos
        self.db = os.path.join(root, 'db')  # here is where we'll clone repos
        self.workdir = os.path.join(root, 'workdir')

        self.repo = []
        self.client = []
        for i in range(count):
            self.repo.append(os.path.join(remote_repos, 'repo' + str(i)))
            self.client.append(os.path.join(client_dir, 'repo' + str(i)))
        os.mkdir(remote_repos)
        os.mkdir(client_dir)
        os.mkdir(root)
        os.mkdir(self.repositories)
        os.mkdir(self.workdir)
        os.mkdir(self.db)
        # create config files
        server_config = {
            'repositories': self.repositories,
            'db': self.db,
            'workdir': self.workdir,
            'agents' : {
                'master' : {
                    'limit' : 1
                }
            }
        }
        with open(self.server_file, 'w') as fh:
            fh.write(yaml.dump(server_config, explicit_start=True, default_flow_style=False))

        # in a subdirectory crete a git repository
        for i in range(count):
            os.mkdir(self.repo[i])
            with cwd(self.repo[i]):
                _system("git init --bare")
            with cwd(client_dir):
                _system("git clone " + self.repo[i])

        user_config['repos'] = []
        for i in range(count):
            user_config['repos'].append({
                    'name': 'repo' + str(i),
                    'branch': 'master',
                    'type': 'git',
                    'url': self.repo[i],
                })

        with open(self.config_file, 'w') as fh:
            fh.write(yaml.dump(user_config, explicit_start=True,  default_flow_style=False))


        # TODO: tests a case where we have 2 repos each with 2 branches and we are usin a non-master branch in the 2nd repository
