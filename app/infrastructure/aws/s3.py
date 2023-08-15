import hashlib
import logging
from io import BytesIO

from boto3_type_annotations.s3 import Client
from botocore.exceptions import ClientError


class S3Service:
    s3_client: Client

    def __init__(self, s3_client: Client) -> None:
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )
        self.s3_client = s3_client

    def get_file_path(self, bucket_name: str, file_path: str) -> str:
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=file_path)
            return file_path
        except ClientError:
            return ""

    def upload_file(
        self, file: BytesIO, user_id: str, bucket_name: str, extension: str
    ) -> str | None:
        hashed_name = hashlib.sha256(file.read()).hexdigest()
        upload_path = f"user/{user_id}/{hashed_name}{extension}"
        path = self.get_file_path(bucket_name, upload_path)
        if path:
            return self.create_pre_signed_url(bucket_name, upload_path)
        file.seek(0)
        self.s3_client.upload_fileobj(
            file,
            Bucket=bucket_name,
            Key=upload_path,
        )
        self.logger.debug(
            "File %s has been successfully uploaded by user %s",
            upload_path,
            user_id,
        )
        return self.create_pre_signed_url(bucket_name, upload_path)

    def get_file(self, file_path: str, bucket_name: str) -> dict:
        try:
            obj = self.s3_client.get_object(Bucket=bucket_name, Key=file_path)
        except ClientError as e:
            self.logger.error(e, exc_info=True)
            return {}
        return obj

    def create_pre_signed_url(
        self, bucket_name: str, object_name: str, expiration: int = 3600
    ) -> str | None:
        """Generate a preSigned URL to share an S3 object
        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """

        # Generate a preSigned URL for the S3 object
        try:
            response = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_name},
                ExpiresIn=expiration,
            )
        except ClientError as e:
            self.logger.error(e)
            return None

        # The response contains the preSigned URL
        return response
