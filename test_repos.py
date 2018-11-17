from mytools import cwd, capture2
import yaml
import os

#import check

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
        assert os.path.exists( os.path.join(self.repos_parent, 'repo0') )
        assert os.listdir( os.path.join(self.repos_parent, 'repo0/') ) == ['.git']
        assert not os.path.exists(os.path.join(self.workdir, '1', 'repo0/'))

        # update the repository
        with cwd(self.client[0]):
            with open('README.txt', 'w') as fh:
                fh.write("first line\n")
            _system("git add .")
            _system("git commit -m 'first' --author 'Foo Bar <foo@bar.com>'")
            _system("git push")
        _system("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug))
        assert os.listdir( os.path.join(self.repos_parent, 'repo0/') ) == ['README.txt', '.git']
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
        assert code == 13, "test failure repored"
        #assert out == "" # TODO: this will fail if --debug is on, but also becaues there is some output from the git commands.
        assert os.listdir( os.path.join(self.repos_parent, 'repo0/') ) == ['selftest.py', '.git']
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
        assert os.listdir( os.path.join(self.repos_parent, 'repo0/') ) == ['selftest.py', '.git']
        assert os.path.exists(os.path.join(self.workdir, '2', 'repo0/'))
        assert os.listdir(os.path.join(self.workdir, '2', 'repo0/')) == ['selftest.py', '.git']


    def setup_repos(self, temp_dir, user_config, count):
        remote_repos = os.path.join(temp_dir, 'remote_repos')  # bare repos
        client_dir = os.path.join(temp_dir, 'client')  # workspace of users
        root = os.path.join(temp_dir, 'server')
        self.server_file = os.path.join(root, 'server.yml')
        self.config_file = os.path.join(root, 'config.yml')  # this might be in a repository
        self.repos_parent = os.path.join(root, 'repos_parent')  # here is where we'll clone repos
        self.workdir = os.path.join(root, 'workdir')

        self.repo = []
        self.client = []
        for i in range(count):
            self.repo.append(os.path.join(remote_repos, 'repo' + str(i)))
            self.client.append(os.path.join(client_dir, 'repo' + str(i)))
        os.mkdir(remote_repos)
        os.mkdir(client_dir)
        os.mkdir(root)
        os.mkdir(self.repos_parent)
        os.mkdir(self.workdir)
        # create config files
        server_config = {
            'root': self.repos_parent,
            'workdir': self.workdir,
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
                    'type': 'git',
                    'url': self.repo[i],
                })

        with open(self.config_file, 'w') as fh:
            fh.write(yaml.dump(user_config, explicit_start=True,  default_flow_style=False))


