from io import BytesIO

import boto3
import hashlib

from app.core import config
from app.utils.utils import logger


class S3Image:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY,
            aws_secret_access_key=config.AWS_SECRET_KEY,
            region_name=config.AWS_REGION
        )
        self.hash_algo = hashlib.sha256()
    
    def check_file_exists(self, bucket_name: str, file_path=str):
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=file_path)
            return file_path
        except:
            return None

    def upload_file(self, file: BytesIO, user_id: str, bucket_name: str):
        hashed_name = hashlib.sha256(file.read()).hexdigest()
        upload_path = f"user/{user_id}/{hashed_name}.jpg"
        path = self.check_file_exists(bucket_name, upload_path)
        if path is not None:
            return path
        file.seek(0)
        try:
            self.s3_client.upload_fileobj(
                file,
                Bucket=bucket_name,
                Key=upload_path,
            )
            return upload_path
        except Exception as e:
            logger.error(e, exc_info=True)
            return None

    def get_file(self, file_path: str, bucket_name: str):
        try:
            obj = self.s3_client.get_object(Bucket=bucket_name, Key=file_path)
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
        return obj
