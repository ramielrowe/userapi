# userapi

 * [API Documentation](#api-documentation)
 * [Development Environment](#development-environment)

### API Documentation

#### GET /users/`<userid>` - Get Specified User
  * Parameters:
    * userid - ID of user to retrieve
  * Example Response Body:
    * `{"userid": "apmelton", "first_name": "Andrew", "last_name": "Melton", "groups": ["admins"]}`
  * Status Codes:
    * 200 - Requested user exists
    * 404 - Requested user does not exist

#### POST /users - Create Specified User
  * Parameters:
    * None
  * Required fields:
    * userid - str
    * first_name - str
    * last_name - str
  * Optional fields:
    * groups - list(str)
      * default - empty list
  * Example Request Body:
    * `{"userid": "apmelton", "first_name": "Andrew", "last_name": "Melton", "groups": ["admins"]}`
  * Example Response Body:
    * `{"userid": "apmelton", "first_name": "Andrew", "last_name": "Melton", "groups": ["admins"]}`
  * Status Codes:
    * 201 - Requested user has been created
    * 400 - Required field missing
    * 409 - User with requested `userid` already exists

#### PUT /users/`<userid>` - Update Specified User
  * Description: Updates the give users fields or groups.
  * Parameters:
    * userid - The ID of the user to update
  * Required fields:
    * userid - str
    * first_name - str
    * last_name - str
  * Optional fields:
    * groups - list(str)
      * default - empty list
  * Example Request Body:
    * `{"userid": "apmelton", "first_name": "Drew", "last_name": "Melton", "groups": ["admins"]}`
  * Example Response Body:
    * `{"userid": "apmelton", "first_name": "Drew", "last_name": "Melton", "groups": ["admins"]}`
  * Status Codes:
    * 201 - Requested user has been created
    * 400 - Required field missing
    * 404 - Requested user does not exist
    * 409 - Requested new `userid` already exists

#### DELETE /users/`<userid>` - Delete Specified User
  * Description: Deletes a user from any groups it is a member of then deletes the user.
  * Parameters:
    * userid - The ID of the user to update
  * Status Codes:
    * 200 - Requested user has been deleted
    * 404 - Requested user does not exist

#### GET /groups/`<name>` - Get Specified Group
  * Description: Returns list of userids of users in specified group.
  * Parameters:
    * name - Name of group to retrieve
  * Example Response Body:
    * `["apmelton", "sflynn", "tron"]`
  * Status Codes:
    * 200 - Requested group exists
    * 404 - Requested group does not exist

#### POST /groups - Create Specified Group
  * Description: Creates an empty group with specified name.
  * Parameters:
    * None
  * Required fields:
    * name - str
  * Example Request Body:
    * `{"name": "admins"}`
  * Example Response Body:
    * `{"name": "admins"}`
  * Status Codes:
    * 201 - Requested group has been created
    * 400 - Required field missing
    * 409 - Group with specified `name` already exists

#### PUT /groups/`name` - Update Members of Specified Group
  * Parameters:
    * name - Name of group to update
  * Required fields:
    * bare list of `userid`s
  * Example Request Body:
    * `["cartman", "kenny", "kyle", "stan"]`
  * Example Response Body:
    * `["cartman", "kenny", "kyle", "stan"]`
  * Status Codes:
    * 200 - Requested group has been updated
    * 400 - Response body is not a list
    * 404 - Requested group or user does not exist

#### DELETE /groups/`name` - Specified Specified Group
  * Description: Removes any users from specified group, then deletes the group
  * Parameters:
    * name - Name of group to delete
  * Status Codes:
    * 200 - Requested group has been deleted
    * 404 - Requested group does not exist

### Development Environment

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
