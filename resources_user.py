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

# Parser for incoming data for forgot password request
parser_forgot_password = reqparse.RequestParser()
parser_forgot_password.add_argument('email', help='This field cannot be blank', required=True)

# Parser for incoming data for password reset request
parser_reset_password = reqparse.RequestParser()
parser_reset_password.add_argument('token', type=str, help='Token is required', required=True, location='form')
parser_reset_password.add_argument('email', type=str, help='Email is required', required=True, location='form')
parser_reset_password.add_argument('new_password', type=str, help='New password is required', required=True, location='form')

parser_all_blogs = reqparse.RequestParser()
parser_all_blogs.add_argument('page', type=int, default=1)
parser_all_blogs.add_argument('per_page', type=int, default=5)
parser_all_blogs.add_argument('last_blog_id', type=int, default=0)
parser_all_blogs.add_argument('last_blog_updated_time', type=str, default=None)

class UserForgotPassword(Resource):
    def post(self):
        data = parser_forgot_password.parse_args()

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
            return {'message': 'Please enter a valid email'}

        user = User.find_by_email(data['email'])
        if not user:
            return {'message': 'Email does not exist'}
        elif not user.verified:
            return {'message': 'Email is not verified'}

        try:
            reset_token = serializer.dumps(data['email'], salt='forgot-password-salt')
            reset_link = api.url_for(UserResetPasswordRequest, token=reset_token, _external=True)
            message = Message(subject='Password Reset - 重置密码', recipients=[data['email']])
            message.html = render_template('password_reset_request.html', reset_link=reset_link)
            mail.send(message)
            return {'message': 'Password reset instructions sent to your email'}, 200
        except Exception as e:
            print(e)
            return {'message': 'Something went wrong'}, 500
        
class UserResetPasswordRequest(Resource):
    def get(self, token):
        try:
            email = serializer.loads(token, salt='forgot-password-salt', max_age=3600)  # Token valid for 1 hour
        except SignatureExpired:
            # render error page
            error_content = render_template('error.html', title="Password Reset", heading="Password Reset Failed", message="The token has expired! Please request a new password reset link.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res
        except BadTimeSignature:
            # render error page
            error_content = render_template('error.html', title="Password Reset", heading="Password Reset Failed", message="The token is invalid! Please request a new password reset link.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res
        
        html_content = render_template('password_reset_page.html', token=token, email=email)
        # Create a response object with the correct Content-Type
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        return response
    
class UserResetPassword(Resource):
    def post(self):
        data = parser_reset_password.parse_args()

        # Verify the token
        try:
            email_from_token = serializer.loads(data['token'], salt='forgot-password-salt', max_age=3600)
            if data['email'] != email_from_token:
                # render error page
                error_content = render_template('error.html', title="Password Reset", heading="Password Reset Failed", message="The token is invalid! Please request a new password reset link.")
                # Create a response object with the correct Content-Type
                err_res = make_response(error_content)
                err_res.headers['Content-Type'] = 'text/html'
                return err_res
        except SignatureExpired:
            # render error page
            error_content = render_template('error.html', title="Password Reset", heading="Password Reset Failed", message="The token has expired! Please request a new password reset link.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res
        except BadTimeSignature:
            # render error page
            error_content = render_template('error.html', title="Password Reset", heading="Password Reset Failed", message="The token is invalid! Please request a new password reset link.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res

        # Find the user by email
        user = User.find_by_email(data['email'])
        if not user:
            # render error page
            error_content = render_template('error.html', title="Password Reset", heading="Password Reset Failed", message="User not found. Please refresh the page and try again.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res
        
        # Update the user's password
        user.password = User.generate_hash(data['new_password'])
        try:
            # save user to database
            user.save_to_db()
        except:
            # render error page
            error_content = render_template('error.html', title="Password Reset", heading="Password Reset Failed", message="Cannot update password now. Please try again later.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res
        
        html_content = render_template('password_reset.html')
        # Create a response object with the correct Content-Type
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        return response

# User click the verification link sent to their email, this endpoint will verify the email
class UserVerifyEmail(Resource):
    def get(self, token):
        try:
            email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)  # Token valid for 1 hour
        except SignatureExpired:
            # render error page
            error_content = render_template('error.html', title="Email Verification", heading="Email Verification Failed", message="The token has expired! Please request a new email verification link.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res
        except BadTimeSignature:
            # render error page
            error_content = render_template('error.html', title="Email Verification", heading="Email Verification Failed", message="The token is invalid! Please request a new email verification link.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res
        
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
            # render error page
            error_content = render_template('error.html', title="Email Verification", heading="Email Verification Failed", message="Cannot update verification now. Please try again later.")
            # Create a response object with the correct Content-Type
            err_res = make_response(error_content)
            err_res.headers['Content-Type'] = 'text/html'
            return err_res

class UserSignUp(Resource):
    def post(self):
        data = parser_signup.parse_args()
        if len(data['username']) < 2:
            return {'message': 'Username must be at least 2 characters long'}
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
            return {'message': 'Please enter a valid email'}
        elif not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', data['password']):
            return {'message': 'Password must be 8+ length with a mix of letters and numbers'}
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
                }, 200
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
                verification_link = api.url_for(UserVerifyEmail, token=token, _external=True)
                message = Message(subject = 'Email Verification - 邮箱验证链接', recipients=[data['email']])
                message.html = render_template('email_verification_request.html', verification_link=verification_link)
                mail.send(message)
                return {
                    'message': 'Verification email sent',
                    'username': new_user.username,
                    'email': new_user.email,
                }, 200
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
        }, 200
      
# refresh token endpoint to get a new access token
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}, 200
      
      
class AllUsers(Resource):
    def get(self):
        return User.return_all()

    # comment this when using in production
    def delete(self):
        return User.delete_all()

    
class UserAllBlogs(Resource):
    @jwt_required()
    def post(self, email):
        data = parser_all_blogs.parse_args()
        return User.find_by_email(email).return_blogs(page=data['page'], per_page=data['per_page'], last_blog_id=data['last_blog_id'], last_blog_updated_time=data['last_blog_updated_time'])