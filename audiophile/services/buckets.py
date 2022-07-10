import logging

from aiobotocore.session import get_session

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self, *, bucket_name, region_name, access_key, secret_key):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.access_key = access_key
        self.secret_key = secret_key

    async def upload_file(self, file_bytes_obj, file):
        session = get_session()
        key = "storages/{}".format(file.filename)
        async with session.create_client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as client:
            file_upload_response = await client.put_object(
                Bucket=self.bucket_name,
                Body=file_bytes_obj,
                Key=key,
            )
            if file_upload_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info(f"File {file.filename} uploaded successfully")
