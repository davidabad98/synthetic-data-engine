import logging
import os
import uuid
from datetime import datetime
from io import StringIO

import boto3
import pandas as pd

from config.config import (
    AWS_PROFILE,
    GENERATED_DATA_DIR,
    S3_INPUT_BUCKET,
    S3_INPUT_BUCKET_FOLDER,
    S3_OUTPUT_PRESIGNED_URL_EXPIRATION,
    UPLOADED_DATA_DIR,
)

logger = logging.getLogger(__name__)
session = boto3.Session(profile_name=AWS_PROFILE)
s3 = session.client("s3")


def generate_filename(file_extension=".csv"):
    return f"{uuid.uuid4()}{file_extension}"


def save_dataframe_to_s3(df, bucket_name, prefix="output/", generate_url=True):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3_key = f"{prefix}{generate_filename()}"

    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())

    if generate_url:
        # Create a pre-signed URL for temporary access
        file_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": s3_key},
            ExpiresIn=S3_OUTPUT_PRESIGNED_URL_EXPIRATION,
        )
        logger.info(f"Uploaded data saved to: {file_url}")
        return file_url

    s3_path = f"s3://{bucket_name}/{s3_key}"

    logger.info(s3_path)
    return s3_path


def save_dataframe_locally(df: pd.DataFrame, folder_path=GENERATED_DATA_DIR):
    """
    Saves the given DataFrame as a CSV file in the specified local folder.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        folder_path (str): The directory where the file will be saved.

    Returns:
        str: The local file path of the saved CSV.
    """
    # Ensure the directory exists
    os.makedirs(folder_path, exist_ok=True)

    # Generate a filename
    file_name = generate_filename()
    file_path = os.path.join(folder_path, file_name)

    # Save the CSV file
    df.to_csv(file_path, index=False)

    logger.info(f"File saved locally: {file_path}")
    return file_path


async def save_uploaded_data_locally(file, content, folder_path=UPLOADED_DATA_DIR):
    """
    Saves the given data file in the specified local folder.

    Args:
        file: The data file to save.
        folder_path (str): The directory where the file will be saved.

    Returns:
        str: The local file path of the saved CSV.
    """
    # Ensure the directory exists
    os.makedirs(folder_path, exist_ok=True)

    # Generate a filename
    file_name = generate_filename()

    # Save file locally
    local_path = os.path.join(folder_path, file_name)
    with open(local_path, "wb") as local_file:
        local_file.write(content)

    logger.info(f"Uploaded data saved locally: {local_path}")

    return {"filename": file.filename, "fileKey": file_name, "fileUrl": local_path}


async def save_uploaded_data_to_s3(
    file,
    content,
    bucket_name=S3_INPUT_BUCKET,
    prefix=S3_INPUT_BUCKET_FOLDER,
):
    # Generate a unique file key
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    new_file_name = generate_filename(file_extension)
    file_key = f"{prefix}/{new_file_name}"

    # Upload directly to S3
    s3.put_object(
        Bucket=bucket_name, Key=file_key, Body=content, ContentType=file.content_type
    )

    # Create a pre-signed URL for temporary access
    file_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": file_key},
        ExpiresIn=180,  # URL valid for 3 minutes
    )
    logger.info(f"Uploaded data saved to: {file_url}")

    return {
        "filename": file.filename,
        "fileKey": file_key,
        "fileUrl": file_url,
        "originalFileName": new_file_name,
    }


def save_text_locally(transcript, folder_path="app/data/generated"):
    # Ensure the directory exists
    os.makedirs(folder_path, exist_ok=True)

    # Generate a filename
    file_name = generate_filename("synthetic_transcript")
    file_path = os.path.join(folder_path, file_name)

    # Save the transcript to a .txt file
    filename = file_path
    with open(filename, "w") as f:
        f.write(transcript)

    return file_path


def save_text_to_s3(text, bucket_name, prefix="output/"):
    # Generate a filename
    file_name = generate_filename("_transcript.txt")
    s3_key = f"{prefix}{file_name}"

    # Create an S3 client
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3 = session.client("s3")

    # Upload the text as a file to S3
    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=text)

    s3_path = f"s3://{bucket_name}/{s3_key}"
    print(f"File saved to {s3_path}")
    return s3_path
