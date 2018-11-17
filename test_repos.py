from mytools import cwd
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
        self.setup_repos(temp_dir)

        user_config = {
            'repos': [
                         {
                             'name' : 'main',
                             'type' : 'git',
                             'url'  : self.repo1,
                         }
                     ]
        }
        with open(self.config_file, 'w') as fh:
            fh.write(yaml.dump(user_config, explicit_start=True,  default_flow_style=False))




        _system("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug))
        assert os.path.exists( os.path.join(self.repos_parent, 'repo1') )
        assert os.listdir( os.path.join(self.repos_parent, 'repo1/') ) == ['.git']
        assert not os.path.exists(os.path.join(self.workdir, '1', 'repo1/'))


    # git rev-parse HEAD

        # update the repository
        with cwd(self.client1):
            with open('README.txt', 'w') as fh:
                fh.write("first line\n")
            _system("git add .")
            _system("git commit -m 'first' --author 'Foo Bar <foo@bar.com>'")
            _system("git push")
        _system("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug))
        assert os.listdir( os.path.join(self.repos_parent, 'repo1/') ) == ['README.txt', '.git']
        assert os.path.exists(os.path.join(self.workdir, '1', 'repo1/'))
        assert os.listdir(os.path.join(self.workdir, '1', 'repo1/')) == ['README.txt', '.git']
        # check if the sha change was noticed

        # create a branch, see if the new branch is noticed
        with cwd(self.client1):
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
        _system("python check.py --server {} --config {} {}".format(self.server_file, self.config_file, debug))

        # first workdir did not change
        assert os.path.exists(os.path.join(self.workdir, '1', 'repo1/'))
        assert os.listdir(os.path.join(self.workdir, '1', 'repo1/')) == ['README.txt', '.git']

        # second workdir has the new file as well
        assert os.path.exists(os.path.join(self.workdir, '2', 'repo1/'))
        assert os.listdir(os.path.join(self.workdir, '2', 'repo1/')) == ['MASTER', 'README.txt', '.git']

        # second workdir has the new file as well
        assert os.path.exists(os.path.join(self.workdir, '3', 'repo1/'))
        assert os.listdir(os.path.join(self.workdir, '3', 'repo1/')) == ['TODO', 'README.txt', '.git']

    def setup_repos(self, temp_dir):
        remote_repos = os.path.join(temp_dir, 'remote_repos')  # bare repos
        client_dir = os.path.join(temp_dir, 'client')  # workspace of users
        root = os.path.join(temp_dir, 'server')
        self.server_file = os.path.join(root, 'server.yml')
        self.config_file = os.path.join(root, 'config.yml')  # this might be in a repository
        self.repos_parent = os.path.join(root, 'repos_parent')  # here is where we'll clone repos
        self.workdir = os.path.join(root, 'workdir')
        self.repo1 = os.path.join(remote_repos, 'repo1')
        self.client1 = os.path.join(client_dir, 'repo1')
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
        os.mkdir(self.repo1)
        with cwd(self.repo1):
            _system("git init --bare")
        with cwd(client_dir):
            _system("git clone " + self.repo1)
