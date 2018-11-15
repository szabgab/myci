import argparse
import yaml
import logging
import re
import os
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
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help="Server config file", required=True)
    parser.add_argument('--config', help="Config file", required=True)
    parser.add_argument('--debug', help="Turn on debugging", action="store_true")
    args = parser.parse_args()

    if args.debug:
        add_logger()

    log.debug("debug")

    log.debug(args.server)
    with open(args.server) as fh:
        server = yaml.load(fh)


    log.debug(args.config)
    with open(args.config) as fh:
        config = yaml.load(fh)

    # TODO: the first time we clone, ssh might want to verify the server an we might need to manually accept it.
    # TODO: How can we automate this?
    #print(config)
    for repo in config['repos']:
        log.debug("Repo url {}".format(repo['url']))
        if repo['type'] != 'git':
            raise Exception("Unsupported repository {}".format(repo['type']))
        m = re.search(r'/([^/]*?)(\.git)?\Z', repo['url'])
        if not m:
            raise Exception("Could not parse repo url '{}'".format(repo['url']))
        repo_local_dir = m.group(1)
        log.debug("Local repo dir {}".format(repo_local_dir))
        # TODO have a root directory for each project that is under the server root
        # TODO allow the user to supply a local directory
        local_repo_path = os.path.join(server['root'], repo_local_dir)
        log.debug("Local repo path {}".format(local_repo_path))

        if not os.path.exists( local_repo_path ):
            log.debug("clone repo for the first time")
            if 'credentials' in repo:
                os.environ['GIT_SSH_COMMAND'] = "ssh -i  " + repo['credentials']
            cmd_list = [git, 'clone', repo['url'], repo_local_dir]
            cmd = ' '.join(cmd_list)
            log.debug(cmd)
            with cwd(server['root']):
                os.system(cmd)
                # get current sha ?? In which branch?
            old_branches = {}
        else:
            log.debug("update repository")
            old_branches = get_branches(local_repo_path)
            cmd_list = [git, 'fetch']
            cmd = ' '.join(cmd_list)
            log.debug(cmd)
            with cwd(local_repo_path):
                os.system(cmd)
        new_branches = get_branches(local_repo_path)
        log.debug(yaml.dump(new_branches))

    # For each watched(!) repo get a list of branches and the sha for each branch before and after the update
    # TODO If sha changed
    # TODO If branch disappeared
    # TODO If new branch appeared

    # using thoses shas:
    #   generate new build number
    #   for each agent:
    #       update the local central repositories
    #       create the new build directory
    #       local clone the repositories, check out the give shas, run the rest of the execution

if __name__ == '__main__':
    main()


