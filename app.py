import datetime
import os
from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from itsdangerous import URLSafeTimedSerializer
from flask_cors import CORS
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

app = Flask(__name__)

# db config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# jwt config
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=1440)  # 1 day
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=43200)  # 30 days
# mail config
app.config['MAIL_SERVER'] = os.environ['MAIL_SERVER']
app.config['MAIL_PORT'] = os.environ['MAIL_PORT']
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = ('Bounden', os.environ['MAIL_USERNAME'])

# Initialize extensions
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
api = Api(app)
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
CORS(app, resources={r"/*": {"origins": ["*", "http://localhost:3000", "https://*.bounden.cn"]}})

@app.before_request
def create_tables():
    # The following line will remove this handler, making it
    # only run on the first request
    app.before_request_funcs[None].remove(create_tables)

    db.create_all()

# Initialize the JWT manager
jwt = JWTManager(app)


import views, resources_user, resources_blog, resources_image, resources_memoryMapMarker

api.add_resource(resources_user.UserVerifyEmail, '/verify_email/<string:token>')
api.add_resource(resources_user.UserForgotPassword, '/forgot_password')
api.add_resource(resources_user.UserResetPasswordRequest, '/reset_password_request/<string:token>')
api.add_resource(resources_user.UserResetPassword, '/reset_password')
api.add_resource(resources_user.UserSignUp, '/signup')
api.add_resource(resources_user.UserSignIn, '/signin')
api.add_resource(resources_user.TokenRefresh, '/token/refresh')
api.add_resource(resources_user.AllUsers, '/users')
api.add_resource(resources_user.UserAllBlogs, '/users/<email>/blogs')

api.add_resource(resources_blog.BlogCreate, '/blogs/create')
api.add_resource(resources_blog.BlogUpdate, '/blogs/edit/<int:id>')
api.add_resource(resources_blog.AllBlogs, '/blogs')
api.add_resource(resources_blog.BlogWithId, '/blogs/<int:id>')
api.add_resource(resources_blog.CommentPost, '/blogs/<int:id>/comments/create')
api.add_resource(resources_blog.CommentWithId, '/blogs/<int:id>/comments/<int:commentId>')
api.add_resource(resources_blog.AllComments, '/blogs/<int:id>/comments')
api.add_resource(resources_blog.CommentReplies, '/blogs/<int:id>/comments/<int:commentId>/replies')

api.add_resource(resources_image.ImageUpload, '/images/upload')

api.add_resource(resources_memoryMapMarker.MemoryMapMarkerCreate, '/memory_map_markers/create')
api.add_resource(resources_memoryMapMarker.MemoryMapMarkerUpdate, '/memory_map_markers/edit')
api.add_resource(resources_memoryMapMarker.MemoryMapMarkerList, '/memory_map_markers/<string:user_email>')
api.add_resource(resources_memoryMapMarker.MemoryMapMarkerDelete, '/memory_map_markers/delete')