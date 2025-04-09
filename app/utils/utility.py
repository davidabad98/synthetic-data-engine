import logging
import os
from datetime import datetime
from io import StringIO

import boto3
import pandas as pd

from config.config import AWS_PROFILE

logger = logging.getLogger(__name__)


def generate_filename(base_name):
    if base_name == "synthetic_data":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{base_name}_{timestamp}.csv"
    elif base_name == "synthetic_transcript":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{base_name}_{timestamp}.txt"
    else:
        raise ValueError("Invalid base name provided for filename generation.")

def save_dataframe_to_s3(df, bucket_name, prefix="output/"):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    file_name = generate_filename("synthetic_data")
    s3_key = f"{prefix}{file_name}"

    session = boto3.Session(profile_name=AWS_PROFILE)
    s3 = session.client("s3")
    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())
    s3_path = f"s3://{bucket_name}/{s3_key}"

    logger.info(s3_path)
    return s3_path


def save_dataframe_locally(df: pd.DataFrame, folder_path="app/data/generated"):
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
    file_name = generate_filename("synthetic_data")
    file_path = os.path.join(folder_path, file_name)

    # Save the CSV file
    df.to_csv(file_path, index=False)

    logger.info(f"File saved locally: {file_path}")
    return file_path


def save_text_locally(transcript,folder_path="app/data/generated"):
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
    file_name = generate_filename("synthetic_transcript")
    s3_key = f"{prefix}{file_name}"

    # Create an S3 client
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3 = session.client("s3")

    # Upload the text as a file to S3
    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=text)

    s3_path = f"s3://{bucket_name}/{s3_key}"
    print(f"File saved to {s3_path}")
    return s3_path