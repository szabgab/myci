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


def test_repo(tmpdir):
    temp_dir = str(tmpdir)
    print(temp_dir)

    remote_repos = os.path.join(str(tmpdir), 'remote_repos') # bare repos
    client_dir   = os.path.join(str(tmpdir), 'client')       # workspace of users

    root         = os.path.join(str(tmpdir), 'server')
    server_file  = os.path.join(root, 'server.yml')
    config_file  = os.path.join(root, 'config.yml')  # this might be in a repository

    repos_parent  = os.path.join(root, 'repos_parent')  # here is where we'll clone repos
    workdir       = os.path.join(root, 'workdir')

    repo1         = os.path.join(remote_repos, 'repo1')
    client1       = os.path.join(client_dir, 'repo1')

    os.mkdir(remote_repos)
    os.mkdir(client_dir)

    os.mkdir(root)
    os.mkdir(repos_parent)
    os.mkdir(workdir)

    # create config files
    server_config = {
        'root':    repos_parent,
        'workdir': workdir,
    }
    with open(server_file, 'w') as fh:
        fh.write(yaml.dump(server_config, explicit_start=True,  default_flow_style=False))

    user_config = {
        'repos': [
                     {
                         'name' : 'main',
                         'type' : 'git',
                         'url'  : repo1,
                     }
                 ]
    }
    with open(config_file, 'w') as fh:
        fh.write(yaml.dump(user_config, explicit_start=True,  default_flow_style=False))


    # in a subdirectory crete a git repository
    os.mkdir(repo1)
    with cwd(repo1):
        _system("git init --bare")
    with cwd(client_dir):
        _system("git clone " + repo1)


    _system("python check.py --server {} --config {} {}".format(server_file, config_file, debug))
    assert os.path.exists( os.path.join(repos_parent, 'repo1') )
    assert os.listdir( os.path.join(repos_parent, 'repo1/') ) == ['.git']
    assert not os.path.exists(os.path.join(workdir, '1', 'repo1/'))


# git rev-parse HEAD

    # update the repository
    with cwd(client1):
        with open('README.txt', 'w') as fh:
            fh.write("first line\n")
        _system("git add .")
        _system("git commit -m 'first' --author 'Foo Bar <foo@bar.com>'")
        _system("git push")
    _system("python check.py --server {} --config {} {}".format(server_file, config_file, debug))
    assert os.listdir( os.path.join(repos_parent, 'repo1/') ) == ['README.txt', '.git']
    assert os.path.exists(os.path.join(workdir, '1', 'repo1/'))
    assert os.listdir(os.path.join(workdir, '1', 'repo1/')) == ['README.txt', '.git']
    # check if the sha change was noticed

    # create a branch, see if the new branch is noticed
    with cwd(client1):
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
    _system("python check.py --server {} --config {} {}".format(server_file, config_file, debug))

    # first workdir did not change
    assert os.path.exists(os.path.join(workdir, '1', 'repo1/'))
    assert os.listdir(os.path.join(workdir, '1', 'repo1/')) == ['README.txt', '.git']

    # second workdir has the new file as well
    assert os.path.exists(os.path.join(workdir, '2', 'repo1/'))
    assert os.listdir(os.path.join(workdir, '2', 'repo1/')) == ['MASTER', 'README.txt', '.git']

    # second workdir has the new file as well
    assert os.path.exists(os.path.join(workdir, '3', 'repo1/'))
    assert os.listdir(os.path.join(workdir, '3', 'repo1/')) == ['TODO', 'README.txt', '.git']
