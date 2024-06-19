import datetime
from models import Image, User, MemoryMapMarker
from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required, get_jwt_identity)

parser_create = reqparse.RequestParser()
parser_create.add_argument('user_email', type=str, required=True, help='User email is required')
parser_create.add_argument('latitude', type=float, required=True, help='Latitude is required')
parser_create.add_argument('longitude', type=float, required=True, help='Longitude is required')

parser_update = reqparse.RequestParser()
parser_update.add_argument('user_email', type=str, required=True, help='User email is required')
parser_update.add_argument('id', type=int, required=True, help='Marker id is required')
parser_update.add_argument('name', type=str)
parser_update.add_argument('description', type=str)
parser_update.add_argument('latitude', type=float, required=True, help='Latitude is required')
parser_update.add_argument('longitude', type=float, required=True, help='Longitude is required')
parser_update.add_argument('images', type=str)

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('user_email', type=str, required=True, help='User email is required')
parser_delete.add_argument('id', type=int, required=True, help='Marker id is required')

class MemoryMapMarkerCreate(Resource):
    @jwt_required()
    def post(self):
        data = parser_create.parse_args()

        if get_jwt_identity() != data['user_email']:
            return {'message': 'You are not authorized'}, 401
        
        user_obj = User.find_by_email(data['user_email'])
        # create a new marker
        new_marker = MemoryMapMarker(
            user=user_obj,
            name="",
            description="",
            latitude=data['latitude'],
            longitude=data['longitude'],
            images="",
            created=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            updated=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )

        # save the marker to the database
        try:
            new_marker.save_to_db()
            return {
                'message': 'Marker created successfully',
                'marker': MemoryMapMarker.to_json(new_marker),
            }
        except:
            return {'message': 'Something went wrong'}, 500
        
class MemoryMapMarkerUpdate(Resource):
    @jwt_required()
    def post(self):
        data = parser_update.parse_args()

        if get_jwt_identity() != data['user_email']:
            return {'message': 'You are not authorized'}, 401
        
        marker = MemoryMapMarker.find_by_id(data['id'])

        if marker:
            marker.name = data['name']
            marker.description = data['description']
            marker.latitude = data['latitude']
            marker.longitude = data['longitude']
            marker.images = data['images']
            marker.updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                marker.save_to_db()
                return {
                   'message': 'Marker updated successfully',
                   'marker': MemoryMapMarker.to_json(marker)
                }
            except:
                return {'message': 'Something went wrong'}, 500
        else:
            return {'message': 'Marker not found'}, 404
        
class MemoryMapMarkerDelete(Resource):
    @jwt_required()
    def delete(self):
        data = parser_delete.parse_args()

        if get_jwt_identity() != data['user_email']:
            return {'message': 'You are not authorized'}, 401
        
        return MemoryMapMarker.delete_by_id(data['id'])

        
class MemoryMapMarkerList(Resource):
    @jwt_required()
    def get(self, user_email):
        if get_jwt_identity() != user_email:
            return {'message': 'You are not authorized'}, 401
        
        user = User.find_by_email(user_email)
        return MemoryMapMarker.return_all_with_user_id(user.id)