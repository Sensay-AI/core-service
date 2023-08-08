import hashlib
from io import BytesIO

import boto3
import botocore
import botocore.exceptions
from singleton_decorator import singleton

from app.core import config
from app.utils.utils import logger


@singleton
class S3Image:
    def __init__(self) -> None:
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=config.AWS_ACCESS_KEY,
            aws_secret_access_key=config.AWS_SECRET_KEY,
            region_name=config.AWS_REGION,
        )
        self.hash_algo = hashlib.sha256()

    def check_file_exists(self, bucket_name: str, file_path: str) -> str:
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=file_path)
            return file_path
        except botocore.exceptions.ClientError:
            return ""

    def upload_file(
        self, file: BytesIO, user_id: str, bucket_name: str, extension: str
    ) -> str:
        hashed_name = hashlib.sha256(file.read()).hexdigest()
        upload_path = f"user/{user_id}/{hashed_name}{extension}"
        path = self.check_file_exists(bucket_name, upload_path)
        if path:
            return path
        file.seek(0)
        try:
            self.s3_client.upload_fileobj(
                file,
                Bucket=bucket_name,
                Key=upload_path,
            )
            return upload_path
        except Exception as error:
            logger.error(error, exc_info=True)
            return ""
