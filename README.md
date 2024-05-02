# BOUNDEN
Blogs and Services (Webservice - Cross-End Support)

## Examples
- [Blog (Deployed onRender)](https://bounden.onrender.com/)

## Requirements
- Ubuntu with sudo privilege (22.04 tested) / Web App deploy services (Render, Heroku, etc.)
- Python3
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
- Activate the virtual environment ```source venv/bin/activate```
- Install the required packages ```pip install -r requirements.txt```
- Initialize the flask database (first time) & run the server ```FLASK_APP=app.py FLASK_DEBUG=1 flask run``` or just ```flask run``` (on port 5000 by default)

## Dependencies
- The whole website is built using React as frontend and Flask + Python as backend
- flask_sqlalchemy is used for the database storage
- react-auth-kit and jwt_extended are used for user authentication and token refreshing
- Quill is used for the blog creater/editor
- Render is used for the deployment and hosting of the website
- Gunicorn is used for the production server

## Deployment ([Render](https://docs.render.com/github))
- ATTENTION: Free - only for test purpose (if you want to push database back to github, fee applies)
- The api website is hosted on a custom domain on Render [Provided URL](https://bounden-api.onrender.com/) (will not work with direct access)
- Follow the instructions on the Render website to link to the github account
- Create a new static site, link to the backend repo on github, set name (the prefix of the provided URL), and other details

## Deployment ([Nginx on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-22-04))
- ATTENTION: only apply to those Ubuntu with sudo privileges
- [Install nginx](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-22-04) on the Ubuntu machine
- Config a domain name to point to the server - an A record with the_domain pointing to the server’s public IP address, and an A record with www.the_domain pointing to the server’s public IP address.
- Allow access to port 5000 ```sudo ufw allow 5000```
### Method 1: Gunicorn only
- Use gunicorn to serve the flask app to port 5000 ```gunicorn --bind 0.0.0.0:5000 wsgi:app```
- Check if service deployed to the port 5000 ```lsof -i :5000```
- Check if port 5000 is allowed (Security Group) on the cloud ubuntu server for TCP connection
- Access the api through the browser with ```<cloud-server-ip>:5000```
### Method 2: Gunicorn with systemd
- [use systemd to auto the process](https://docs.gunicorn.org/en/stable/deploy.html#systemd) [more reference](https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd)
- Setup the service ```sudo vi /etc/systemd/system/bounden.service```
```
[Unit]
Description=Gunicorn instance to serve <project-name>
After=network.target

[Service]
User=jonas
WorkingDirectory=/home/jonas/<project-name>
Environment="PATH=/home/jonas/<project-name>/venv/bin"
ExecStart=/home/jonas/<project-name>/venv/bin/gunicorn -b 0.0.0.0:5000 -w 4  wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```
- Every time you change the content of ```<project-name>.service```, run ```sudo systemctl daemon-reload```
- Start the service ```sudo systemctl start <project-name>``` or restart the service ```sudo systemctl restart <project-name>```
- Check the status of the service ```sudo systemctl status bounden```
- Check the log of systemd ```journalctl -u bounden```
- Check if service deployed to the port 5000 ```lsof -i :5000```
- Check if port 5000 is allowed (Security Group) on the cloud ubuntu server for TCP connection and do ```sudo ufw allow 5000``` on the shell of the server
- Access the api through the browser with ```<cloud-server-ip>:5000```


## Support
This is an open source project and everyone is welcome to contribute. Feel free to open an issue, if you have any questions or incase you find a bug. Also if you are impressed/inspired by this project, a little credit will be much appreciated.
Created by [Jonas](https://github.com/lujiannan) with ❤️