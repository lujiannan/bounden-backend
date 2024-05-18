from app import db
from passlib.hash import pbkdf2_sha256 as sha256

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
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Blog {self.title}>"
    
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
            # content is not required for blog list (performance optimization)
        }

    @classmethod
    def return_all(cls):
        return {'blogs': list(map(lambda blog: cls.__preview_to_json(blog), cls.query.all()))}
    
    @classmethod
    def get_paginated_blogs(cls, page, per_page):
        """
        Get blogs sorted by updated time with pagination.

        :param page: The page number (1-indexed).
        :param per_page: Number of blogs per page.
        :return: A dictionary with paginated blogs.
        """
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
            num_rows_deleted = db.session.query(cls).filter_by(id = id).delete()
            db.session.commit()
            return {'message': f'{num_rows_deleted} row(s) deleted'}
        except:
            return {'message': 'Something went wrong'}
    
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

    def __repr__(self):
        return f"<User {self.email}>"
    
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
    def return_blogs(self, page, per_page):
        """
        Get blogs sorted by updated time with pagination.

        :param page: The page number (1-indexed).
        :param per_page: Number of blogs per page.
        :return: A dictionary with paginated blogs.
        """
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
