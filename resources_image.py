from models import Image, Blog, User
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
# Access token we need to access protected routes. Refresh token we need to reissue access token when it will expire.
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)

# for uploading images to COS bucket
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = os.environ['COS_SECRET_ID']     # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = os.environ['COS_SECRET_KEY']   # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
region = 'ap-nanjing'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填


config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)
bucket = 'bounden-1312559530'

parser_upload = reqparse.RequestParser()
parser_upload.add_argument('user_email', type=str, help = 'This field cannot be blank', required = True, location = 'form')
parser_upload.add_argument('name', type=str, help = 'This field cannot be blank', required = True, location = 'form')
parser_upload.add_argument('file', type=FileStorage, help = 'This field cannot be blank', required = True, location = 'files')

class ImageUpload(Resource):
    @jwt_required()
    def post(self):
        data = parser_upload.parse_args()
        response = client.put_object(
            Bucket=bucket,
            Body=data.file,
            Key='blog-images/' + data.user_email + '/' + data.name,
            StorageClass='STANDARD',
            EnableMD5=False
        )
        if response['ETag'] != None:
            author_obj = User.find_by_email(data.user_email)
            if not author_obj:
                return {
                    'message': 'Author not found'
                }
            
            new_image = Image(
                name = data.name,
                user = author_obj,
                url = 'https://' + bucket + '.cos.' + region + '.myqcloud.com/blog-images/' + data.user_email + '/' + data.name,
            )
            # save the new blog object to the database
            try:
                new_image.save_to_db()
                return {
                    'message': 'Image uploaded successfully',
                    'url': 'https://' + bucket + '.cos.' + region + '.myqcloud.com/blog-images/' + data.user_email + '/' + data.name,
                }
            except:
                return {'message': 'Something went wrong'}, 500
        else:
            return {
                'message': 'Image upload failed'
            }
        