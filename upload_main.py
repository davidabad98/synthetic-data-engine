from epic import EPICPromptGenerator
from request_model import *
import os
import utility
import config
def main(model_used):
    n_samples=3 
    generated_rows=10
    # Define the path to the CSV file
    #file_path = os.path.join(os.path.dirname(__file__), 'app', 'data', 'sample_data', 'CustomerClaimsDataset.csv')
    file_path = config.S3_INPUT_FILEPATH
    #file_path = "CustomerClaimsDataset.csv"  # Replace with your dataset file
    # Calling the EPICPromptGenerator class
    epic_generator = EPICPromptGenerator(file_path,n_samples, generated_rows)
    # Generating an epic prompt
    epic_prompt = epic_generator.generate_prompt()
    # Creating an instance of the requestModel class
    sm = requestModel()
    # Sending a request to the model based on the model_used argument
    if model_used == 'titan':
        df = sm.send_request_titan(epic_prompt)
    elif model_used == 'groq':
        df = sm.send_request_groq(epic_prompt)
    else:
        raise ValueError("Invalid model_used argument. Please specify either 'titan' or 'groq'.")
    
    destination_uri = utility.save_dataframe_to_s3(df, bucket_name = config.S3_OUTPUT_BUCKET, prefix = config.S3_OUTPUT_FOLDER)

    return destination_uri
if __name__ == "__main__":
    main(model_used='titan')  # Change to 'groq' to use the Groq API