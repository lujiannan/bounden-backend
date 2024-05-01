# BOUNDEN
Blogs and Services (Webservice - Cross-End Support)

## Examples
- [Blog (Deployed onRender)](https://bounden.onrender.com/)

## Requirements
- Ubuntu (22.04 tested)
- Python3
- NPM
- VS Code or any other code editor

## Project Start Guide
### Clone the repository
```
sudo apt-get install git (check: git --version)
git config --global user.name "******"
git config --global user.email "******"

git clone https://github.com/lujiannan/bounden-backend.git
```

### Server Setup
- Go to the server directory
- Install python virtual envrionment base ```sudo apt-get install python3.10-venv```
- Check for upgrades ```sudo apt upgrade```
- Create the python virtual environment ```python3 -m venv venv```
#### Method 1: step by step
- Go to the server directory
- Activate the virtual environment ```source venv/bin/activate```
- Install the required packages ```pip install -r requirements.txt```
- Initialize the flask database (first time) & run the server ```FLASK_APP=run.py FLASK_DEBUG=1 flask run``` (on port 5000 by default)
#### Method 2: client-side npm run
- Go to the client directory
- Run the server ```npm run server-start``` (on port 5000 by default)

## Dependencies
- The whole website is built using React as frontend and Flask + Python as backend
- flask_sqlalchemy is used for the database storage
- react-auth-kit and jwt_extended are used for user authentication and token refreshing
- Quill is used for the blog creater/editor

## Support
This is an open source project and everyone is welcome to contribute. Feel free to open an issue, if you have any questions or incase you find a bug. Also if you are impressed/inspired by this project, a little credit will be much appreciated.
Created by [Jonas](https://github.com/lujiannan) with ❤️