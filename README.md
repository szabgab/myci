# Repos

Some CI system


## TODO

* Send notifications
* Create a web application to show the build director
* Run steps (test)
* Execute the whole thing on a remote machine to which we have passwordless ssh access


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

