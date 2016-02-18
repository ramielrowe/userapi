userapi
=======

Development environment
-----------------------

The following guide has been tested on Ubuntu 14.04 with Docker 1.10.

`userapi` uses Docker to simplify deployment and development. So, our first step is to install Docker.

    $ curl -sSL https://get.docker.com/ | sh  # install latest docker version
    ...
    $ sudo docker info  $ check status of docker daemon after installation
    Containers: 0
     Running: 0
     Paused: 0
     Stopped: 0
    Images: 0
    Server Version: 1.10.1
    ...

Next, you can clone down the `userapi` repository and begin setting up your environment.

    $ git clone https://github.com/ramielrowe/userapi.git
    $ cd userapi
    $ sudo ./deploy_postgres.sh  # Sets up a bare PostgreSQL instance, only needs to happen once
    $ sudo ./deploy_api.sh  # Builds userapi image, creates tables in PostgreSQL, and deploys the api.
    $ curl http://$(sudo docker port dev_userapi_api 8000)/users/a  # test the api
    {
      "code": 404, 
      "exception": "UserNotFoundException"
    }

You now have a fully working API, but to run unit and functional tests you will need some depenencies installed.

    $ sudo apt-get update && sudo apt-get install python python-dev python-pip libpq-dev -y
    $ sudo pip install tox

Running unit tests

    $ tox -epy27
    ...
    ================================================================= test session starts ==================================================================
    platform linux2 -- Python 2.7.6, pytest-2.8.7, py-1.4.31, pluggy-0.3.1
    rootdir: /home/apmelton/userapi, inifile: 
    collected 44 items 
    
    test-requirements.txt s
    userapi/tests/unit/test_api.py .................
    userapi/tests/unit/db/test_api.py ..........................
    
    ========================================================= 43 passed, 1 skipped in 0.32 seconds =========================================================
    _______________________________________________________________________ summary ________________________________________________________________________
      py27: commands succeeded
      congratulations :)
  
  Running functional tests
  
    $ sudo ./run_functional.sh
    ================================================================= test session starts ==================================================================
    platform linux2 -- Python 2.7.6, pytest-2.8.7, py-1.4.31, pluggy-0.3.1
    rootdir: /home/apmelton/userapi, inifile: 
    collected 24 items 
    
    test-requirements.txt s
    userapi/tests/functional/test_api.py .......................
    
    ========================================================= 23 passed, 1 skipped in 0.64 seconds =========================================================
    _______________________________________________________________________ summary ________________________________________________________________________
      functional: commands succeeded
      congratulations :)
  
  When you make changes, simply run `deploy_api.sh` again to push out the new changes.
