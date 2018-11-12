
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
