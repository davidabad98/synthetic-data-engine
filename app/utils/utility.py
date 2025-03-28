import os
from datetime import datetime
from io import StringIO

import boto3
import pandas as pd

from config.config import AWS_PROFILE


def generate_filename(base_name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{base_name}_{timestamp}.csv"


def save_dataframe_to_s3(df, bucket_name, prefix="output/"):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    file_name = generate_filename("synthetic_data")
    s3_key = f"{prefix}{file_name}"

    session = boto3.Session(profile_name=AWS_PROFILE)
    s3 = session.client("s3")
    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())
    s3_path = f"s3://{bucket_name}/{s3_key}"

    print(s3_path)
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

    print(f"File saved locally: {file_path}")
    return file_path
