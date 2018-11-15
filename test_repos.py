from mytools import cwd
import yaml
import os

#import check

def test_repo(tmpdir):
    root = str(tmpdir)
    print(root)

    server_file = os.path.join(root, 'server.yml')
    config_file = os.path.join(root, 'config.yml')
    repos_parent  = os.path.join(root, 'repos_parent')  # here is where we'll clone repos
    workdir       = os.path.join(root, 'workdir')

    repo1 = os.path.join(root, 'repo1')


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
        os.system("git init")  # TODO this should be a bare repo and we should have a client dir as well

    # create another subdirectory for root
    os.mkdir(repos_parent)
    os.system("python check.py --server {} --config {}".format(server_file, config_file))
    assert os.path.exists( os.path.join(repos_parent, 'repo1') )
    # check if the cloning is was successful (there should be a master branch) or maybe not as we plan to have this as a bare repo

    # update the repository
    # check.py
    # check if the sha change was noticed

    # create a branch
    # check.py
    # test if the new branch is noticed

