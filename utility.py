import boto3
import pandas as pd
from io import StringIO
from datetime import datetime

def generate_filename(base_name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{base_name}_{timestamp}.csv"

def save_dataframe_to_s3(df, bucket_name, prefix='output/'):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    file_name = generate_filename("synthetic_data")
    s3_key = f"{prefix}{file_name}"
    
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=csv_buffer.getvalue()
    )

    return f"s3://{bucket_name}/{s3_key}"