# Repos

Some CI system


## TODO

* Move the results.json to the db directory and call it id.json
* Base the web application on the db directory
* Shall we create the directories listed in the server config file or shall we expect the user to create them? What right should they have? 
    - repositories
    

* Include the commit messages of the respective sha1 values in both the log file and the reporting json

* Send notifications
* Create a web application to show the build directory
* Save artifacts
* Execute the whole thing on a remote machine to which we have passwordless ssh access
* When we notice an update, generate a list of execution modes (each one has a bunch of parameters, an agentm and a sub-build number)
* On each agent set up the git repository as necessary with the appropriate sha values.
* Run the steps on each agent
* Have a post process to collect the results.

* Test what happens if the server.yml config file is missing, or if some of the parameters are missing, or if the directories don't exist or if they are not writable.


## Plan


* Configure generic repositories with credentials needed to read from them.
* the system will clone the repository to some central place

* Add some triggers:
     * Run at a given time no matter what (crontab like config)
     * Run at a given time if there were changes (crontab like config)
     * Get a callback from the git repository to know when to run
     * Manual trigger via some web interface.
     * ...

* Create a root directory for the current job
* clone the central repo into the root directory of the current job
* ...
* Remove the root directory of the job 

* Alternative cleanup: Keep the N most recent build directories around

* A list of steps to execute, each one should probably be a comand line script

* Mode 1: We have a central git repository with the configuration of the server and the jobs we would like to run on it.
* Mode 2: In the central configuration we have the pointer to the repositories and each repository has its own configurations. (But then maybe there is not need for monitoring other repositories?)


## Development of the web application


```
CI_SERVER_CONFIG_FILE=server.yml  FLASK_APP=web.app FLASK_DEBUG=1 flask run --host 0.0.0.0
```


## Deployment

This is just one possibility

* Create a "micro" sized instance in Google Cloud Platform (0.6 Gb memory)
* Install Ubuntu 18.10 on a 10 Gb disk
* SSH to that machine

```
mkdir work
mkdir work/repos_parent
mkdir work/build_parent
git clone https://github.com/szabgab/repos.git
```

```
pip install -r requirements.txt
```

Add the following line to the crontab:

```
* * * * * python3 repos/check.py --server repos/server.yml --config repos/config.yml
```

(Run crontab -e and replace all the comment lines with the line above)


Update and upgrade packages (just normal sysadmin stuff)

```
sudo apt-get update
sudo apt-get upgrade
```

Install mail client and server  (accept the defaults)

```
sudo apt-get install mailutils
```

## Configuration


### server.yml

* repositories: Path to the parent directory where we'll keep clones of all the repositories. (Currently all the repos are immediately under this, but we might create a subdirectory for each user/project to)
* workdir: parent directory of each build. (Each build will get its own directory where we'll have copies of the checked out repositories) Based on a configuration parameter we might automatically remove old direcroties
* artifacts: location where we store all the artifacst. Each build will get its own directory here. This directory will also have a cleanup policy, separate from the build directory. Only files that are supposed to be part of a release should go here.
* db: Path to the "database" of the builds. Here we'll store the meta information about each build. We have a file called "counter.txt" that has the number of the most recent build.

