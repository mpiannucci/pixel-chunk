import argparse
import boto3


def clear_bucket(bucket_name):
    try:
        # Create S3 client
        s3 = boto3.client("s3")

        # List all objects in bucket
        paginator = s3.get_paginator("list_objects_v2")

        # Delete all objects
        for page in paginator.paginate(Bucket=bucket_name):
            if "Contents" in page:
                objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
                s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})

        print(f"Successfully cleared all objects from bucket: {bucket_name}")

    except Exception as e:
        print(f"Error clearing bucket: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clear all objects from an S3 bucket")
    parser.add_argument("bucket", help="Name of the S3 bucket to clear")
    args = parser.parse_args()

    clear_bucket(args.bucket)
