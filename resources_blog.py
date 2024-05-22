import datetime
from models import User, Blog
from flask_restful import Resource, reqparse
# Access token we need to access protected routes. Refresh token we need to reissue access token when it will expire.
from flask_jwt_extended import jwt_required, get_jwt_identity

# add parsing of incoming data inside the POST request
# required fields are marked as required=True
parser_create = reqparse.RequestParser()
parser_create.add_argument('category', type=str, required=True, help='Category is required')
parser_create.add_argument('title', type=str, required=True, help='Title is required')
parser_create.add_argument('description', type=str, required=False)
parser_create.add_argument('author_email', type=str, required=True, help='Author_email is required')
parser_create.add_argument('content', type=str, required=True, help='Content is required')

parser_all = reqparse.RequestParser()
parser_all.add_argument('page', type=int, default=1)
parser_all.add_argument('per_page', type=int, default=5)
parser_all.add_argument('last_blog_id', type=int, default=0)
parser_all.add_argument('last_blog_updated_time', type=str, default=None)

class BlogCreate(Resource):
    @jwt_required()
    def post(self):
        data = parser_create.parse_args()

        if get_jwt_identity() != data['author_email']:
            return {'message': 'You are not authorized'}, 401

        author_obj = User.find_by_email(data['author_email'])
        # create a new blog object with the data from the request
        new_blog = Blog(
            category=data['category'],
            title=data['title'],
            description=data['description'],
            created=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            updated=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            author=author_obj,
            content=data['content']
        )

        # save the new blog object to the database
        try:
            new_blog.save_to_db()
            return {
                'message': 'Blog {} created successfully'.format( data['title']),
            }
        except:
            return {'message': 'Something went wrong'}, 500
        
class BlogUpdate(Resource):
    @jwt_required()
    def post(self, id):
        data = parser_create.parse_args()

        if get_jwt_identity() != data['author_email']:
            return {'message': 'You are not authorized'}, 401

        blog_obj = Blog.find_by_id(id)

        if blog_obj:
            blog_obj.category = data['category']
            blog_obj.title = data['title']
            blog_obj.description = data['description']
            blog_obj.updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            blog_obj.content = data['content']

            try:
                blog_obj.save_to_db()
                return {
                    'message': 'Blog {} updated successfully'.format( data['title']),
                }
            except:
                return {'message': 'Something went wrong'}, 500
        else:
            return {'message': 'Blog not found'}, 404
    
class AllBlogs(Resource):
    def post(self):
        data = parser_all.parse_args()
        return Blog.get_paginated_blogs(page=data['page'], per_page=data['per_page'], last_blog_id=data['last_blog_id'], last_blog_updated_time=data['last_blog_updated_time'])
    
    # comment this when using in production
    def delete(self):
        return Blog.delete_all()
    
class BlogWithId(Resource):
    def get(self, id):
        return Blog.find_by_id(id, requireJson=True)

    @jwt_required()
    def delete(self, id):
        email = Blog.find_by_id(id).author.email
        if email != get_jwt_identity():
            return {'message': 'You are not authorized'}, 401
        return Blog.delete_by_id(id)