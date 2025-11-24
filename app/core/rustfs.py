import boto3
from botocore.config import Config
from app.core.config import settings


# optional: tweak signature version or retries
boto_config = Config(signature_version="s3v4", retries={"max_attempts": 3})


rustfs_s3_client = boto3.client(
    "s3",
    endpoint_url=settings.RUSTFS_ENDPOINT,
    aws_access_key_id=settings.RUSTFS_ACCESS_KEY,
    aws_secret_access_key=settings.RUSTFS_SECRET_KEY,
    config=boto_config,
)


# helper to ensure bucket exists (best-effort)
def ensure_bucket(bucket_name=settings.RUSTFS_BUCKET):
    try:
        rustfs_s3_client.head_bucket(Bucket=bucket_name)
    except Exception:
        try:
            rustfs_s3_client.create_bucket(Bucket=bucket_name)
        except Exception:
            # some S3-compatible providers might not allow create; ignore
            pass
