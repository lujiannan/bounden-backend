# BOUNDEN
Blogs and Services (Webservice - Cross-End Support)

## Examples
- [Blog (Deployed on Render)](https://bounden.onrender.com/)

## Requirements
- Ubuntu with sudo privilege (22.04 tested) / Web App deploy services (Render, Heroku, etc.)
- Python3
- Sqlite3
- COS storage server (腾讯云COS is used in this project)
- VS Code or any other code editor

## Known Issues
- None

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
- Install Sqlite for debugging database ```sudo apt install sqlite```
- Check for upgrades ```sudo apt upgrade```
- Create the python virtual environment ```python3 -m venv venv```
- Activate the virtual environment ```source venv/bin/activate```
- Install the required packages ```pip install -r requirements.txt```
- (Dev) Initialize the flask database (first time) & run the server ```FLASK_APP=app.py FLASK_DEBUG=1 flask run``` or just ```flask run``` (on port 5000 by default)

## Dependencies
- The whole website is built using React as frontend and Flask + Python as backend
- flask_sqlalchemy is used for the database storage
- react-auth-kit and jwt_extended are used for user authentication and token refreshing
- Quill is used for the blog creater/editor
- Render is used for the deployment and hosting of the website
- Gunicorn is used for the production server

## Deployment - [Render](https://docs.render.com/github)
- ATTENTION: Free - only for test purpose (if you want to push database back to github, fee applies)
- The api website is hosted on a custom domain on Render [Provided URL](https://bounden-api.onrender.com/) (will not work with direct access)
- Follow the instructions on the Render website to link to the github account
- Create a new site, link to the backend repo on github, set name (the prefix of the provided URL), and other details
- set environment variables on the site (based on the .env file)

## Deployment - [Nginx on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04)
- ATTENTION: only apply to those Ubuntu with sudo privileges
- [Install nginx](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-22-04) on the Ubuntu machine
- Config a domain name to point to the server - an A record with api.the_domain pointing to the server’s public IP address
- Enable the ufw (firewall) ```sudo ufw enable```
- Allow access to port 5000 ```sudo ufw allow 5000```
### Method 1: Gunicorn only
- Use gunicorn to serve the flask app to port 5000 ```gunicorn --bind 0.0.0.0:5000 -w 4 wsgi:app```
- Check if service deployed to the port 5000 ```lsof -i :5000```
- Check if port 5000 is allowed (Security Group) on the cloud ubuntu server for TCP connection
- Access the api through the browser with ```http://<cloud-server-ip>:5000```
- (tips) kill gunicorn ```pkill gunicorn```
### Method 2: Gunicorn managed by Systemd
- [use systemd to auto the process](https://docs.gunicorn.org/en/stable/deploy.html#systemd) / [more reference 1st](https://blog.miguelgrinberg.com/post/how-to-deploy-a-react--flask-project) / [more reference 2nd](https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd)
- Setup the service ```sudo vi /etc/systemd/system/bounden.service```
```
[Unit]
Description=Gunicorn instance to serve <project-directory-name>
After=network.target

[Service]
User=<user>
Group=<user>
WorkingDirectory=/home/<user>/<project-directory-name>
Environment="PATH=/home/<user>/<project-directory-name>/venv/bin"
ExecStart=/home/<user>/<project-directory-name>/venv/bin/gunicorn -b 0.0.0.0:5000 -w 4  wsgi:app
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
- Access the api through the browser with ```http://<cloud-server-ip>:5000```
### Continue on [configuring Nginx to proxy requests](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04#step-5-configuring-nginx-to-proxy-requests)
- Config Nginx site ```sudo vi /etc/nginx/sites-available/<project-name>```
```
server {
        listen 80;
        server_name <configured-domain-for-backend-api>;

        location / {
                include proxy_params;
                proxy_pass http://localhost:5000;
        }
}
```
- Link the file to the sites-enabled dir ```sudo ln -s /etc/nginx/sites-available/<project-name> /etc/nginx/sites-enabled```
- Test for syntax error ```sudo nginx -t```
- Restart the Nginx process for new config ```sudo systemctl restart nginx```
- adjust the firewall ```sudo ufw delete allow 5000 && sudo ufw allow 'Nginx Full'```
- Now navigation to domain on the browser is available ```http://<configured-domain-for-backend-api>:5000```
### Continue on [securing the application to https:// with Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04#step-5-configuring-nginx-to-proxy-requests)
- Install Certbot's Nginx package ```sudo apt install python3-certbot-nginx```
- Use the plugin ```sudo certbot --nginx -d <configured-domain-for-backend-api>```
- HTTP is no longer required ```sudo ufw delete allow 'Nginx HTTP'```

## Support
This is an open source project and everyone is welcome to contribute. Feel free to open an issue, if you have any questions or incase you find a bug. Also if you are impressed/inspired by this project, a little credit will be much appreciated.
Created by [Jonas](https://github.com/lujiannan) with ❤️