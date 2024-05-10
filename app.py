import datetime
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/*": {"origins": ["*", "http://localhost:3000", "https://*.bounden.cn"]}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jonaswebsecretkey'

app.config['JWT_SECRET_KEY'] = 'jonaswebjwtsecretkey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=1440)  # 1 day
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=43200)  # 30 days

db = SQLAlchemy(app)

@app.before_request
def create_tables():
    # The following line will remove this handler, making it
    # only run on the first request
    app.before_request_funcs[None].remove(create_tables)

    db.create_all()

# Initialize the JWT manager
jwt = JWTManager(app)


import views, resources_user, resources_blog, resources_image

api.add_resource(resources_user.UserSignUp, '/signup')
api.add_resource(resources_user.UserSignIn, '/signin')
api.add_resource(resources_user.TokenRefresh, '/token/refresh')
api.add_resource(resources_user.AllUsers, '/users')
api.add_resource(resources_user.UserAllBlogs, '/users/<email>/blogs')

api.add_resource(resources_blog.BlogCreate, '/blogs/create')
api.add_resource(resources_blog.AllBlogs, '/blogs')
api.add_resource(resources_blog.BlogWithId, '/blogs/<int:id>')

api.add_resource(resources_image.ImageUpload, '/images/upload')