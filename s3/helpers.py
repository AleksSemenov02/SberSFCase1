from s3 import s3
from settings import S3


async def ensure_bucket_exists(bucket_name: str):
    async with s3.client(
        service_name="s3",
        endpoint_url=S3.endpoint_url,
    ) as client:
        try:
            await client.head_bucket(Bucket=bucket_name)
            return True
        except client.exceptions.ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                try:
                    await client.create_bucket(Bucket=bucket_name)
                    return True
                except client.exceptions.ClientError as e:
                    return False
            else:
                return False
