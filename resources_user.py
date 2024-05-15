from models import User
from flask_restful import Resource, reqparse
# Access token we need to access protected routes. Refresh token we need to reissue access token when it will expire.
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
from flask_mail import Message
from app import mail
import os
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
    def get(self, email):
        user = User.find_by_email(email)
        if user:
            user.verified = True
        try:
            # save user to database
            user.save_to_db()
            return {'message': 'Email verified successfully'}
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
        
        if user:
            # update user's password if already exists
            print(data['password'])
            user.username = data['username']
            user.password = User.generate_hash(data['password'])

            try:
                # save user to database
                user.save_to_db()
                # send verification email
                message = Message(subject = 'Email Verification Link - 邮箱验证链接', recipients=[data['email']])
                message.body = 'Please verify your email by clicking on the link - 请点击链接验证您的邮箱: \n {}/verify_email/{}'.format(os.environ['BACKEND_URL'], data['email'])
                mail.send(message)
                return {
                    'message': 'User with email {} was created'.format( data['email']),
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
                message = Message(subject = 'Email Verification Link - 邮箱验证链接', recipients=[data['email']])
                message.body = 'Please verify your email by clicking on the link - 请点击链接验证您的邮箱: \n {}/verify_email/{}'.format(os.environ['BACKEND_URL'], data['email'])
                mail.send(message)
                # access_token = create_access_token(identity = data['email'])
                # refresh_token = create_refresh_token(identity = data['email'])
                return {
                    'message': 'User with email {} was created'.format( data['email']),
                    # 'access_token': access_token,
                    # 'refresh_token': refresh_token,
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