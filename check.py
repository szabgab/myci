import argparse
import yaml
import logging
import re
import os
import fcntl
#import subprocess
from mytools import cwd

git = 'git'


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

def add_logger():
    logger = logging.getLogger(__name__)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)-10s - %(message)s'))
    logger.addHandler(sh)

# given path to a repository return a dictionary where the keys are branch names
# the values are the sha1 of each branch
def get_branches(path):
    branches = {}
    with cwd(path):
        os.system("git pack-refs --all")
        if os.path.exists('.git/packed-refs'):
            # It seems the file does not exist if the repository is empty
            with open('.git/packed-refs') as fh:
                for line in fh:
                    if re.search(r'\A#', line):
                        continue
                    m = re.search(r'\A(\S+)\s+refs/remotes/origin/(.*)', line)
                    if m:
                        branches[ m.group(2) ] = m.group(1)
    return branches



def main():
    setup_logger()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help="Server config file", required=True)
    parser.add_argument('--config', help="Config file", required=True)
    parser.add_argument('--debug', help="Turn on debugging", action="store_true")
    args = parser.parse_args()

    if args.debug:
        add_logger()

    logger.debug("debug")

    logger.debug(args.server)
    with open(args.server) as fh:
        server = yaml.load(fh)


    logger.debug(args.config)
    with open(args.config) as fh:
        config = yaml.load(fh)

    old_branches, new_branches = update_central_repos(config, server)

    # For each watched(!) repo get a list of branches and the sha for each branch before and after the update.
    # If each repo can have multiple branches then shall we really build all the combinations or should there be
    # a leading repository
    # I think we need to assume that one of the repositories is under test and the others have fixed branches
    # TODO If sha changed
    # TODO If branch disappeared
    # TODO If new branch appeared

    for branch in sorted(new_branches.keys()):
        if branch in old_branches:
            if old_branches[branch] == new_branches[branch]:
                pass
            else:
                logger.debug("Branch {} changed.".format(branch))
                build(server, config, new_branches[branch])
        else:
            logger.debug("New branch seen: {}".format(branch))
            build(server, config, new_branches[branch])

def get_next_build_number(server):
    counter_file = os.path.join(server['root'], 'counter.txt')
    if os.path.exists(counter_file):
        with open(counter_file, 'r+') as fh:
            fcntl.lockf(fh, fcntl.LOCK_EX)
            count = int(fh.read())
            count += 1
            fh.seek(0, os.SEEK_SET)
            fh.write(str(count))
    else:
        with open(counter_file, 'w') as fh:
            fcntl.lockf(fh, fcntl.LOCK_EX)
            count = 1
            fh.write(str(count))
    return count

def build(server, config, sha1):
    logger = logging.getLogger(__name__)
    build_number = get_next_build_number(server)
    logger.debug("Build number: {}".format(build_number))
    # TODO store the build in some queue and also allow the parallel execution of jobs on agents

    # update_local_repositories()
    build_directory = os.path.join(server['workdir'], str(build_number))
    logger.debug("Build dir: {}".format(build_directory))
    os.mkdir(build_directory)
    with cwd(build_directory):
        for repo in config['repos']:
            logger.debug("Clone the repositories")
            repo_local_name = get_repo_local_name(repo)
            cmd_list = [git, 'clone', os.path.join(server['root'], repo_local_name), repo_local_name]
            cmd = ' '.join(cmd_list)
            logger.debug(cmd)
            os.system(cmd)
            with cwd(repo_local_name):
                logger.debug("Check out the given shas")
                cmd_list = [git, 'checkout', sha1]
                cmd = ' '.join(cmd_list)
                logger.debug(cmd)
                os.system(cmd)
        # TODO: run the steps defined in the configuration

def get_repo_local_name(repo):
    m = re.search(r'/([^/]*?)(\.git)?\Z', repo['url'])
    if not m:
        raise Exception("Could not parse repo url '{}'".format(repo['url']))
    return m.group(1)

def update_central_repos(config, server):
    logger = logging.getLogger(__name__)

    # TODO: the first time we clone, ssh might want to verify the server an we might need to manually accept it.
    # TODO: How can we automate this?
    # print(config)
    for repo in config['repos']:
        logger.debug("Repo url {}".format(repo['url']))
        if repo['type'] != 'git':
            raise Exception("Unsupported repository {}".format(repo['type']))

        repo_local_name = get_repo_local_name(repo)

        logger.debug("Local repo dir {}".format(repo_local_name))
        # TODO have a root directory for each project that is under the server root
        # TODO allow the user to supply a local directory
        local_repo_path = os.path.join(server['root'], repo_local_name)
        logger.debug("Local repo path {}".format(local_repo_path))

        if not os.path.exists(local_repo_path):
            logger.debug("clone repo for the first time")
            if 'credentials' in repo:
                os.environ['GIT_SSH_COMMAND'] = "ssh -i  " + repo['credentials']
            cmd_list = [git, 'clone', repo['url'], repo_local_name]
            cmd = ' '.join(cmd_list)
            logger.debug(cmd)
            with cwd(server['root']):
                os.system(cmd)
                # get current sha ?? In which branch?
            old_branches = {}
        else:
            logger.debug("update repository")
            old_branches = get_branches(local_repo_path)
            cmd_list = [git, 'pull']
            cmd = ' '.join(cmd_list)
            logger.debug(cmd)
            with cwd(local_repo_path):
                os.system(cmd)
        new_branches = get_branches(local_repo_path)
        logger.debug(yaml.dump(new_branches))
    return old_branches, new_branches


if __name__ == '__main__':
    main()


