from models import User
from flask import render_template, make_response
from flask_restful import Resource, reqparse
# Access token we need to access protected routes. Refresh token we need to reissue access token when it will expire.
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
from flask_mail import Message
from itsdangerous import SignatureExpired, BadTimeSignature
from app import mail, serializer, api
# for email validation
import re

# add parsing of incoming data inside the POST request
# required fields are username, email and password
parser_signup = reqparse.RequestParser()
parser_signup.add_argument('username', help = 'This field cannot be blank', required = True)
parser_signup.add_argument('email', help = 'This field cannot be blank', required = True)
parser_signup.add_argument('password', help = 'This field cannot be blank', required = True)

parser_signin = reqparse.RequestParser()
parser_signin.add_argument('email', help = 'This field cannot be blank', required = True)
parser_signin.add_argument('password', help = 'This field cannot be blank', required = True)

# User click the verification link sent to their email, this endpoint will verify the email
class UserVerifyEmail(Resource):
    def get(self, token):
        try:
            email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)  # Token valid for 1 hour
        except SignatureExpired:
            return {'message': 'The token has expired!'}, 400
        except BadTimeSignature:
            return {'message': 'The token is invalid!'}, 400
        
        user = User.find_by_email(email)
        if user:
            user.verified = True
        try:
            # save user to database
            user.save_to_db()
            # render verification email template while user click the link in their email
            html_content = render_template('email_verified.html', email=email)
            # Create a response object with the correct Content-Type
            response = make_response(html_content)
            response.headers['Content-Type'] = 'text/html'
            return response
        except:
            return {'message': 'Something went wrong'}, 500

class UserSignUp(Resource):
    def post(self):
        data = parser_signup.parse_args()
        if len(data['username']) < 2:
            return {'message': 'Username must be at least 2 characters long'}
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
            return {'message': 'Please enter a valid email'}
        elif len(data['password']) < 4:
            return {'message': 'Password must be at least 4 characters long'}
        # check if user already exists
        user = User.find_by_email(data['email'])
        if user and user.verified:
            return {'message': 'Email already exists'. format(data['email'])}
        
        # create a verification token for the user
        token = serializer.dumps(data['email'], salt='email-confirm-salt')
        # create a new user object and save it to the database
        if user:
            # update user's password if already exists
            user.username = data['username']
            user.password = User.generate_hash(data['password'])
            try:
                # save user to database
                user.save_to_db()
                # send verification email
                verification_link = api.url_for(UserVerifyEmail, token=token, _external=True)
                message = Message(subject = 'Email Verification - 邮箱验证链接', recipients=[data['email']])
                message.html = render_template('email_verification_request.html', verification_link=verification_link)
                mail.send(message)
                return {
                    'message': 'Verification email sent',
                    'username': user.username,
                    'email': user.email,
                }
            except:
                return {'message': 'Something went wrong'}, 500
        else:
            # create a new user object if not already exists and verified
            new_user = User(
                username = data['username'],
                email = data['email'],
                password = User.generate_hash(data['password']),
            )

            try:
                # save user to database
                new_user.save_to_db()
                # send verification email
                verification_link = url_for('verify_email', token=token, _external=True)
                message = Message(subject = 'Email Verification - 邮箱验证链接', recipients=[data['email']])
                message.html = render_template('email_verification_request.html', verification_link=verification_link)
                mail.send(message)
                return {
                    'message': 'Verification email sent',
                    'username': new_user.username,
                    'email': new_user.email,
                }
            except:
                return {'message': 'Something went wrong'}, 500


class UserSignIn(Resource):
    def post(self):
        data = parser_signin.parse_args()

        # check if user exists through his email
        current_user = User.find_by_email(data['email'])
        if not current_user:
            return {'message': 'Email does not exist'}
        
        # check if password is correct
        if not User.verify_hash(data['password'], current_user.password):
            return {'message': 'Password is incorrect'}
        
        if not current_user.verified:
            return {'message': 'Email is not verified'}
      
        access_token = create_access_token(identity = data['email'])
        refresh_token = create_refresh_token(identity = data['email'])
        return {
            'message': 'Logged in as {}'.format(current_user.username),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'username': current_user.username,
            'email': current_user.email,
        }
      
# refresh token endpoint to get a new access token
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}
      
      
class AllUsers(Resource):
    def get(self):
        return User.return_all()

    # comment this when using in production
    def delete(self):
        return User.delete_all()

    
class UserAllBlogs(Resource):
    @jwt_required()
    def get(self, email):
        return User.find_by_email(email).return_all_blogs()