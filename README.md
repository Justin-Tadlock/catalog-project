# catalog-project
An application that provides a list of items within a variety of categories as well as providing the user with registration and authentication system through Google Sign-in. Registered users will have the ability to post, edit and delete their own items.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

To run the VM, you must have the following:
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/)
* Python3 is installed on the Vagrant VM
* openssl installed for generating a certificate for HTTPS.

For more information on the base setup, visit the [Udacity VM Setup](https://github.com/udacity/fullstack-nanodegree-vm)

#### A project created in your Google Dev console. 
0. The Dev Console can be found [here](https://console.developers.google.com)
1. Create a project
2. Go to your credentials. The root link is [here](https://console.developers.google.com/apis/credentials)
3. Click "Create credentials", then "OAuth client ID"
4. Select "Web Application"
5. Give the credentials a name (such as "catalog-project-creds")
6. Under "Authorized JavaScript origins", add "https://localhost:5000" and hit Enter
7. Under "Authorized redirect URIs", add "https://localhost:5000/oauthcallback" and hit Enter
8. Click the "**Create**" button
9. You are done with this step, move on to "Running the VM" section.

#### You will need to download the credentials json file from your Google Dev Console
1. Go to your Google Dev Console Credentials section [here](https://console.developers.google.com/apis/credentials)
2. Go to the credentials you created in the Pre-Req section, on the far right click the **DOWN** arrow to download the credentials in json format
3. Go to the location the file was downloaded, rename the file "client_secrets.json"
4. Copy-paste the "client_secrets.json" file into your **catalog-project** app directory.
5. You are done with this step

#### You will also require a "secret_key.txt" file to be made and have some text inside it.
1. In your catalog-project app directory create a "secret_key.txt" file.
2. Open the file and type some text
3. Save the file and close the file.
4. You are done with this step

#### You will need to generate your own self-signed certificates to eliminate security warnings
1. Open cmd prompt/terminal in your project's directory and run
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```
2. Answer the questions that are required for generating the certificate
3. You're done.

## Running the VM

To run the VM you must do the following:
1. Obtain a copy of the repository from: [Repo Zip](https://github.com/udacity/fullstack-nanodegree-vm/archive/master.zip)
2. Unzip the master.zip file into a chosen directory
3. Obtain a copy of this repository from [here](https://github.com/Justin-Tadlock/catalog-project/archive/master.zip) 
4. Unzip the content into the Vagrant's repository directory under "{repoLocation}/vagrant/catalog-project"
5. Open a command prompt/PowerShell/terminal window inside the vagrant directory
6. Run the following commands
```
vagrant init
vagrant up
vagrant ssh
```
7. Once the vagrant VM is running, navigate to the **catalog-project** app directory
``` 
cd /vagrant/catalog-project 
```

**In order for the application to work, you must install the appropriate modules on your vagrant VM:**
```
sudo pip3 install --upgrade -r requirements.txt
```


## Running the server

#### Set up the data

Run the following commands to set up the data used to initialize the database values:
```
python3 ./database_setup.py
python3 ./init_catalog_items.py
```
**NOTE:** You only have to do this once when you first run the app or if you delete the **catalog_data.db** file.

#### Run the web server that hosts the application

Running the following command will launch the app.
```
python3 ./start_catalog_server.py
```

## Browsing the application

On your host machine, open up your browser and navigate to:
```
https://localhost:5000
```

Now you will be able to browse around the application project and utilize all the CRUD functionality once you have authenticated through Google Sign-In.

#### The application also has API endpoints
You can make API calls to the application to view the data in JSON format.

Some examples of API calls are as follows:
* /api/all/categories
* /api/all/subCategories
* /api/all/items
* /api/category/#
* /api/subCategory/#
* /api/item/#
* /api/all/users
** **NOTE: Requires authentication**

**NOTES**:
* # is the id of the item you want to view


## Built With

* [Python](https://www.python.org/downloads/) - Python is a programming language that lets you work quickly and integrate systems more effectively
* [Flask](https://palletsprojects.com/p/flask/) - A lightweight WSGI web application framework.
* [SQLAlchemy](https://www.sqlalchemy.org/) - The Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
* HTML
* CSS


## Authors

* **[Justin-Tadlock](https://github.com/Justin-Tadlock)** - *Initial work*


## Acknowledgments

* [Udacity VM Setup](https://github.com/udacity/fullstack-nanodegree-vm) - for the initial setup of the Vagrant VM.
* [HTTPS Certificates](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)
* [My Auth-Playground Repo](https://github.com/Justin-Tadlock/auth-playground)
* [Integrating Google Sign-In](https://developers.google.com/identity/sign-in/web/sign-in)
* [Color Palette](https://www.materialpalette.com/teal/blue)
* Images and links are found from searching amazon and using their respective URIs for images
