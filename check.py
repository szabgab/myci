import argparse
import yaml
import logging
import re
import os
from contextlib import contextmanager

git = 'git'

@contextmanager
def cwd(path):
    oldpwd=os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)-10s - %(message)s'))
    logger.addHandler(sh)


def main():
    setup_logger()
    log = logging.getLogger(__name__)
    log.debug("debug")

    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help="Server config file", required=True)
    parser.add_argument('--config', help="Config file", required=True)
    args = parser.parse_args()

    log.debug(args.server)
    with open(args.server) as fh:
        server = yaml.load(fh)


    log.debug(args.config)
    with open(args.config) as fh:
        config = yaml.load(fh)

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
        else:
            log.debug("update repository")
            cmd_list = [git, 'fetch']
            cmd = ' '.join(cmd_list)
            log.debug(cmd)
            with cwd(local_repo_path):
                os.system(cmd)

    # if any of the watched repositories have changed then take the sha of each, and start a new build
    # using thoses shas:
    #   generate new build number
    #   for each agent:
    #       update the local central repositories
    #       create the new build directory
    #       local clone the repositories, check out the give shas, run the rest of the execution

main()


