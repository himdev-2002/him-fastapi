from io import BytesIO
from typing import BinaryIO
from app.core.config import settings
from app.utils.logger import log_api
from app.core.rustfs import rustfs_s3_client, ensure_bucket
import os
import sys
import threading

ACT = "rustfs"

def upload_file_to_rustfs(file_obj: BinaryIO | BytesIO, bucket_name: str, key: str, content_type: str, size: int, filename: str):
    log_api(f"Calling utils::rustfs::upload_file_to_rustfs", level="INFO", act=ACT)
    try:
        # Create boto3 S3 client for RustFS (S3-compatible).
        ensure_bucket(bucket_name)
        rustfs_s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            key,
            ExtraArgs={"ContentType": content_type},
            Callback=ProgressPercentageFileObject(file_obj,filename, size)
        )
        return True
    except Exception as e:
        log_api(f"Error uploading file to rustfs: {e}", level="ERROR", act=ACT)
        return False

def remove_file_from_rustfs(key: str, bucket_name: str):
    log_api(f"Calling utils::rustfs::remove_file_from_rustfs", level="INFO", act=ACT)
    try:
        rustfs_s3_client.delete_object(
            Bucket=bucket_name,
            Key=key
        )
        return True
    except Exception as e:
        log_api(f"Error removing file from rustfs: {e}", level="ERROR", act=ACT)
        return False

class ProgressPercentageFile(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r\n%s  %s / %s  (%.2f%%)\r\n" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

class ProgressPercentageFileObject(object):

    def __init__(self, file_obj: BinaryIO | BytesIO, filename: str, size: int):
        self._file_obj = file_obj
        self._size = float(size)
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._filename = filename

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            try:
                percentage = (self._seen_so_far / self._size) * 100
                sys.stdout.write(
                    "\r\n%s  %s / %s  (%.2f%%)\r\n" % (
                        self._filename, self._seen_so_far, self._size,
                        percentage))
            except Exception as e:
                log_api(f"Error writing progress: {e}", level="DEBUG", act=ACT)
            sys.stdout.flush()