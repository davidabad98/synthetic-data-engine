import pandas as pd
import random
import string
import re
import boto3
from collections import defaultdict
from io import StringIO
class EPICPromptGenerator:
    def __init__(self, file_path, n_samples=5,generated_rows = 5, file_type='csv'):
        self.file_path = file_path
        self.n_samples = n_samples
        self.df = self.load_dataset()
        self.categorical_mappings = {}
        self.continuous_stats = {}
        self.file_type = file_type
        self.generated_rows = generated_rows
        
        self.df, self.categorical_mappings, self.continuous_stats = self.process_data()

    def load_dataset(self):
        """ Load dataset either from local file or S3 """
        if self.file_path.startswith('s3://'):
            # Reading from S3
            return self.load_from_s3()
        else:
            # Reading from local file
            return self.load_from_local()
        
    def load_from_local(self):
        try:
            df = pd.read_csv(self.file_path, parse_dates=True)
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file '{self.file_path}' not found. Please check the path.")
        return df
    
    def load_from_s3(self):
        """ Load data from S3 """
        # Extract bucket and object path from the s3 file path
        s3 = boto3.client('s3')
        bucket_name, object_key = self.extract_bucket_and_key(self.file_path)

        try:
            # Get the object from S3
            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            # Read the CSV file from the S3 response
            df = pd.read_csv(StringIO(response['Body'].read().decode('utf-8')), parse_dates=True)
        except Exception as e:
            raise FileNotFoundError(f"Failed to load file from S3. Error: {e}")
        
        return df

    def extract_bucket_and_key(self, s3_uri):
        """ Extract bucket name and file key from s3 URI """
        s3_uri = s3_uri.replace("s3://", "")
        bucket_name, object_key = s3_uri.split("/", 1)
        return bucket_name, object_key

    def clean_text(self, text):
        """ Remove special characters like commas and semicolons from text """
        return re.sub(r'[;,]', '', str(text))

    def process_data(self):
        mapping = {}
        continuous_stats = {}
        
        potential_categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        categorical_cols = [
            col for col in potential_categorical_cols 
            if self.df[col].nunique() < 0.4 * len(self.df)
        ]

        continuous_cols = self.df.select_dtypes(include=['number']).columns

        for col in potential_categorical_cols:
            self.df[col] = self.df[col].apply(self.clean_text)

        for col in categorical_cols:
            unique_values = self.df[col].unique()
            mapping[col] = list(unique_values)  # Store original values for prompt

        if not continuous_cols.empty:
            stats_df = self.df[continuous_cols].describe().T[['mean', 'std', 'min', 'max']].round(2)
            continuous_stats = stats_df.to_dict(orient='index')
        
        return self.df, mapping, continuous_stats
    
    def generate_dynamic_json_format(self):
        """Dynamically create JSON structure based on dataset columns"""
        json_template = "{\n"
        for col in self.df.columns:
            key = col.strip().replace(' ', '_').replace(':', '').replace('-', '_')
            json_template += f'    "{col}": <{key}>,\n'
        json_template = json_template.rstrip(",\n") + "\n}"  # Remove trailing comma
        return json_template

    def sample_data(self):
        sampled_rows = []

        # Collect samples for each unique value in categorical columns
        for col in self.categorical_mappings:
            unique_values = self.df[col].unique()
            for value in unique_values:
                sample_row = self.df[self.df[col] == value].sample(1).iloc[0].to_dict()
                sampled_rows.append(sample_row)

        # If too many samples, limit to 5 with random selection
        if len(sampled_rows) > self.n_samples:
            sampled_rows = random.sample(sampled_rows, self.n_samples)

        # Correct format for dictionary structure
        formatted_sample_data = defaultdict(list)
        for sample in sampled_rows:
            for k, v in sample.items():
                formatted_sample_data[k].append(v)

        return dict(formatted_sample_data)

    def generate_prompt(self):
        feature_names = self.df.columns.tolist()
        
        prompt = "### EPIC Structured Prompt ###\n"
        prompt += f"Features: {', '.join(feature_names)}\n\n"

        if self.continuous_stats:
            prompt += "### Continuous Feature Summary ###\n"
            for col, stats in self.continuous_stats.items():
                prompt += f"{col}: Mean={stats.get('mean', 'N/A')}, Std={stats.get('std', 'N/A')}, Min={stats.get('min', 'N/A')}, Max={stats.get('max', 'N/A')}\n"
            prompt += "\n"

        if self.categorical_mappings:
            prompt += "### Categorical Feature Summary ###\n"
            for col, values in self.categorical_mappings.items():
                prompt += f"{col}: {', '.join(map(str, values))}\n"
            prompt += "\n"

        # Dictionary-based sample data with values in square brackets
        prompt += "### Sample Data in Dictionary Format ###\n"
        sample_data = self.sample_data()

        # Correctly format sample data
        formatted_sample_data = {
            k: [v] if not isinstance(v, list) else v for k, v in sample_data.items()
        }

        prompt += f"{formatted_sample_data}\n\n"
        prompt += "### Requirements ###\n"
        prompt += "I want to generate exactly {} new rows of synthetic data in {} format. \n".format(self.generated_rows, self.file_type)
        prompt += "Include headers only once.\n"
        prompt += "Enclose the data entirely within backticks for easy extraction.\n"
        prompt += "Do not provide explanations, code samples, or additional text. Only provide the data.\n"
        prompt += "Example format:`Name, Address, City, Province, Postal Code, Policy Number, Type of Claim, Claim Code, Approval Status, Date of Service, Date of Claim Submission, Amount Billed, Amount Approved, Provider Name, Provider Address \nJohn Doe, 123 Main St, Toronto, ON, M5J 2N8, SL123456, Dental, D001, Approved, 2025-01-01, 2025-02-01, 200.50, 150.00, DentalCare, 789 King St`\n"
        prompt += "Continuous variables should have the distribution mentioned in Continuous Feature Summary.\n"
        prompt += "The categorical columns should only have the variables available Categorical Feature Summary.\n"
        prompt += "Try to maintain the relationship between variables shown in sample data.\n"
        prompt += "Ensure that generated rows do not repeat the sample data and provide unique entries.\n".format(self.generated_rows)

        return prompt

if __name__ == "__main__":
    file_path = "CustomerClaimsDataset.csv"  # Replace with your dataset file

    epic_generator = EPICPromptGenerator(file_path, n_samples=5)
    epic_prompt = epic_generator.generate_prompt()

    print(epic_prompt)  # Output the structured prompt
