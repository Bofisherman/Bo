import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

s3 = boto3.client('s3',
                  region_name=AWS_REGION,
                  aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_SECRET_KEY)

def upload_file_to_s3(file_obj, filename, folder="uploads", public=True):
    try:
        s3_path = f"{folder}/{filename}"

        extra_args = {
            "ContentType": file_obj.content_type
        }

        # Don't include ACL if bucket has ACLs disabled
        # If you want to control access, use a bucket policy or signed URLs
        s3.upload_fileobj(
            file_obj,
            BUCKET_NAME,
            s3_path,
            ExtraArgs=extra_args
        )

        # This assumes bucket policy allows public read
        url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_path}"
        return url

    except NoCredentialsError:
        raise Exception("S3 credentials not found")
    except Exception as e:
        raise e
