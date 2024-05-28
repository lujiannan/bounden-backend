from app import db
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import func

# Define the Blog model
class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created = db.Column(db.String(10), nullable=False)
    updated = db.Column(db.String(10))
    # foregin key to the author table (lower case table name 'users')
    # when you are operating on the blog data, put param author='<user's name>', it would be automatically linked to users table and mapped to the author_id
    # if you want to know the author's fields (name, email, etc.), you can use the author.field_name
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cover_image = db.Column(db.String(255), default='')
    content = db.Column(db.Text, nullable=False)
    # Define a relationship with the Comment table and create a new column blog as backref
    comments = db.relationship('Comment', backref='blog')
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    # private to_json method to convert the blog object to a json format
    @classmethod
    def __detail_to_json(cls, blog):
        return {
            'id': blog.id,
            'attributes': {
                'title': blog.title,
                'description': blog.description,
                'category': blog.category,
                'created': blog.created,
                'updated': blog.updated,
            },
            'author': {
                'id': blog.author.id,
                'name': blog.author.username,
                'email': blog.author.email,
            },
            'cover_image': blog.cover_image,
            'content': blog.content,
        }
    
    # private to_json method to convert the blog object to a json format
    @classmethod
    def __preview_to_json(cls, blog):
        return {
            'id': blog.id,
            'attributes': {
                'title': blog.title,
                'description': blog.description,
                'category': blog.category,
                'created': blog.created,
                'updated': blog.updated,
            },
            'author': {
                'id': blog.author.id,
                'name': blog.author.username,
                'email': blog.author.email,
            },
            'cover_image': blog.cover_image,
            # content is not required for blog list (performance optimization)
        }

    @classmethod
    def return_all(cls):
        return {'blogs': list(map(lambda blog: cls.__preview_to_json(blog), cls.query.all()))}
    
    @classmethod
    def get_paginated_blogs(cls, page, per_page, last_blog_id, last_blog_updated_time):
        """
        Get blogs sorted by updated time with pagination.
        (always use last_blog_updated_time & last_blog_id to filter blogs, and return the first page with per_page blogs)

        :param page: The page number (1-indexed).
        :param per_page: Number of blogs per page.
        :param last_blog_id: The id of the last blog on the last page.
        :param last_blog_updated_time: The updated time of the last blog on the last page.
        :return: A dictionary with paginated blogs.
        """
        if last_blog_updated_time:
            paginated_blogs = cls.query.filter(cls.updated <= last_blog_updated_time, cls.id != last_blog_id).order_by(cls.updated.desc()).paginate(page=page, per_page=per_page, error_out=False)
        else:
            paginated_blogs = cls.query.order_by(cls.updated.desc()).paginate(page=page, per_page=per_page, error_out=False)
        blogs = paginated_blogs.items

        return {
            'blogs': list(map(lambda blog: cls.__preview_to_json(blog), blogs)),
            'total': paginated_blogs.total,
            'pages': paginated_blogs.pages,
            'current_page': paginated_blogs.page,
            'per_page': paginated_blogs.per_page,
            'has_next': paginated_blogs.has_next,
            'has_prev': paginated_blogs.has_prev,
        }
    
    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': f'{num_rows_deleted} row(s) deleted'}
        except:
            return {'message': 'Something went wrong'}
        
    @classmethod
    def find_by_id(cls, id, requireJson=False):
        the_blog = cls.query.filter_by(id = id).first()
        if requireJson:
            return {'blog': cls.__detail_to_json(the_blog)}
        else:
            return the_blog
    
    @classmethod
    def delete_by_id(cls, id):
        try:
            num_rows_deleted = cls.query.filter_by(id = id).delete()
            Comment.query.filter_by(blog_id = id).delete()
            db.session.commit()
            return {'message': f'{num_rows_deleted} row(s) deleted'}
        except:
            return {'message': 'Something went wrong'}
        
    # Function to count the number of parts in a split string by '.'
    @classmethod
    def _count_parts(cls, column, delimiter='.'):
        return func.length(column) - func.length(func.replace(column, delimiter, '')) + 1
    
    @classmethod
    def get_comments(cls, blogId):
        # Filter comments with len(comment['path'].split('.')) == 1
        comments = Comment.query.filter(Comment.blog_id == blogId).filter(cls._count_parts(Comment.path) == 1).order_by(Comment.id.desc()).all()
        # filtered_comments = [comment for comment in comments if len(comment.path.split('.')) == 1]
        return {'comments': list(map(lambda comment: comment.to_json(), comments))}
    
    @classmethod
    def get_comment_replies(cls, blogId, commentPath):
        # filter replies for a specific comment under blogId, and order them by their path and id in ascending order
        replies = Comment.query.filter(Comment.blog_id == blogId).filter(Comment.path.startswith(commentPath)).filter(cls._count_parts(Comment.path) > 1).order_by(Comment.path, Comment.id).all()
        return {'replies': list(map(lambda reply: reply.to_json(), replies))}

    
# Define the Author model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    # Define a relationship with the Blog table and create a new column author as backref
    blogs = db.relationship('Blog', backref='author')
    images = db.relationship('Image', backref='user')
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()
    
    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'id': x.id,
                'username': x.username,
                'email': x.email,
            }

        return {'users': list(map(lambda x: to_json(x), User.query.all()))}
    
    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': f'{num_rows_deleted} row(s) deleted'}
        except:
            return {'message': 'Something went wrong'}
    
    # return all blogs of a specific user
    def return_blogs(self, page, per_page, last_blog_id, last_blog_updated_time):
        """
        Get blogs sorted by updated time with pagination.
        (always use last_blog_updated_time & last_blog_id to filter blogs, and return the first page with per_page blogs)

        :param page: The page number (1-indexed).
        :param per_page: Number of blogs per page.
        :param last_blog_id: The id of the last blog on the last page.
        :param last_blog_updated_time: The updated time of the last blog on the last page.
        :return: A dictionary with paginated blogs.
        """
        if last_blog_updated_time:
            paginated_blogs = Blog.query.filter_by(author_id = self.id).filter(Blog.updated <= last_blog_updated_time, Blog.id != last_blog_id).order_by(Blog.updated.desc()).paginate(page=page, per_page=per_page, error_out=False)
        else:
            paginated_blogs = Blog.query.filter_by(author_id = self.id).order_by(Blog.updated.desc()).paginate(page=page, per_page=per_page, error_out=False)
        blogs = paginated_blogs.items

        # return all attributes of the blogs except content (performance optimization)
        def to_json(blog):
            return {
                'id': blog.id,
                'attributes': {
                    'title': blog.title,
                    'description': blog.description,
                    'category': blog.category,
                    'created': blog.created,
                    'updated': blog.updated,
                },
                'author': {
                    'id': blog.author.id,
                    'name': blog.author.username,
                    'email': blog.author.email,
                },
                'cover_image': blog.cover_image,
                # content is not required for blog list (performance optimization)
            }
        
        return {
            'blogs': list(map(lambda blog: to_json(blog), blogs)),
            'total': paginated_blogs.total,
            'pages': paginated_blogs.pages,
            'current_page': paginated_blogs.page,
            'per_page': paginated_blogs.per_page,
            'has_next': paginated_blogs.has_next,
            'has_prev': paginated_blogs.has_prev,
        }
        
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
    
class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # private to_json method to convert the blog object to a json format
    @classmethod
    def __to_json(cls, image):
        return {
            'id': image.id,
            'name': image.name,
            'user': {
                'id': image.user.id,
                'username': image.user.username,
                'email': image.user.email,
            },
            'image_url': image.image_url,
        }
    
    @classmethod
    def return_all(cls):
        return {'images': list(map(lambda image: cls.__to_json(image), cls.query.all()))}

class Comment(db.Model):
    __tablename__ = 'comments'

    # support up to 10^8 comments per blog
    _N = 8

    id = db.Column(db.Integer, primary_key=True)
    # foregin key to the blog table (lower case table name 'blogs')
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.String(10), nullable=False, index=True)
    path = db.Column(db.Text, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    replies = db.relationship(
        'Comment', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic')
    
    def to_json(self):
        return {
            'id': self.id,
            'blog_id': self.blog_id,
            'name': self.name,
            'email': self.email,
            'content': self.content,
            'created': self.created,
            'path': self.path,
            'level': self.level(),
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent else None,
            'replyNum': self.get_comment_replies_num(),
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        if not self.path:
            prefix = self.parent.path + '.' if self.parent else ''
            self.path = prefix + '{:0{}d}'.format(self.id, self._N)
            db.session.commit()

    def level(self):
        if self.path:
            # level starts from 1, which represents the indentation of the comment
            return len(self.path.split('.'))
        return None

    def get_comment_replies_num(self):
        return Comment.query.filter(Comment.path.startswith(self.path + '.')).count()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def delete_by_path(cls, commentPath):
        try:
            num_rows_deleted = cls.query.filter(Comment.path.startswith(commentPath)).delete()
            db.session.commit()
            return {'message': f'{num_rows_deleted} row(s) deleted'}
        except:
            return {'message': 'Something went wrong'}