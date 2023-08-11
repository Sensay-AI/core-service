import hashlib
from io import BytesIO

import boto3
from boto3_type_annotations.s3 import Client
from botocore.exceptions import ClientError, NoCredentialsError, ParamValidationError
from singleton_decorator import singleton

from app.core import config
from app.utils.utils import logger


@singleton
class S3Image:
    s3_client: Client

    def __init__(self) -> None:
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=config.AWS_ACCESS_KEY,
            aws_secret_access_key=config.AWS_SECRET_KEY,
            region_name=config.AWS_REGION,
        )

    def check_file_exists(self, bucket_name: str, file_path: str) -> str:
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=file_path)
            return file_path
        except ClientError:
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
        except NoCredentialsError:
            logger.error("AWS credentials not found or invalid.", exc_info=True)
        except ClientError as e:
            logger.error(f"An error occurred when uploading: {e}", exc_info=True)
        except ParamValidationError as e:
            logger.error(
                f"Invalid parameters provided to s3 file upload: {e}", exc_info=True
            )
        except ValueError as e:
            logger.error(f"ValueError: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return ""

    def get_file(self, file_path: str, bucket_name: str) -> dict:
        try:
            obj = self.s3_client.get_object(Bucket=bucket_name, Key=file_path)
        except ClientError as e:
            logger.error(e, exc_info=True)
            return {}
        return obj
