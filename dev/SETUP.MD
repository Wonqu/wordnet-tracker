# Minimal setup steps for development environment
###### Assuming the user is on Ubuntu 18.04 or Windows10 with Python and pip is installed (will probably work for other environments that use docker correctly)
###### To install everything, do steps 1-4
###### To run application locally, do 5-6
##### 1. download [wordnet database](http://ws.clarin-pl.eu/public/wordnet-work.LATEST.sql.gz)
##### 2. extract into mysql/wordnet-work.LATEST.sql
##### 3. install required tools
```
pip install pew docker docker-compose
```
##### 4. set up pew environment named docker
```
pew new docker
```
##### 5. use virtual environment in shell
```
pew workon docker
```
##### 6. run following command in wordnet-tracker directory:
```
cd dev
docker-compose up
```

###### You should be able to connect to [localhost:9000](localhost:9000) and login with following credentials:
###### username: `admin`
###### password: `admin`
###### To close application stop container with keyboard interrupt (`ctrl+c`)
