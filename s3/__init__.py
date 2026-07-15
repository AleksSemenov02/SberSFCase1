import aioboto3

from settings import S3

s3 = aioboto3.Session(
    aws_access_key_id=S3.aws_access_key_id,
    aws_secret_access_key=S3.aws_secret_access_key,
)
