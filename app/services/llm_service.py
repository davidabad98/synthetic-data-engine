# app/services/llm_service.py
import json

import requests

from app.services.request_model import RequestModel
from config.config import LLM_BEDROCK_MODEL_ID, LLM_LOCAL_URL, SERVER_MODE


class LLMService:
    @staticmethod
    def call_llm_api(prompt, max_tokens=3000, temperature=0.5, top_p=0.9):
        """
        Calls the appropriate LLM API based on SERVER_MODE.
        """
        if SERVER_MODE == "local":
            return LLMService.call_local_llm(prompt, max_tokens, temperature, top_p)
        else:
            # old call
            # return LLMService.call_bedrock_llm(prompt, max_tokens, temperature, top_p)
            return LLMService.call_bedrock_llm(prompt, max_tokens, temperature, top_p)

    @staticmethod
    def call_local_llm(prompt, max_tokens, temperature, top_p):
        """
        Calls the local LLM (DeepSeekR1).
        """
        url = LLM_LOCAL_URL
        headers = {"Content-Type": "application/json"}
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "model": "deepseek-r1-distill-llama-8b",  # Critical for LM Studio
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["text"]
        except requests.exceptions.RequestException as e:
            print("Error calling local LLM API:", e)
            return "ERROR"

    @staticmethod
    def call_bedrock_llm(prompt, max_tokens, temperature, top_p):
        """
        Calls the LLM using AWS Bedrock API.
        This is a stub example – replace with actual boto3 calls and response handling.
        """
        import boto3

        bedrock_client = boto3.client("bedrock-runtime")
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        try:
            response = bedrock_client.invoke_model(
                modelId=LLM_BEDROCK_MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload),
            )
            # For this example, we assume the response body contains the generated text.
            generated_text = response["body"].read().decode("utf-8")
            return generated_text
        except Exception as e:
            print("Error calling Bedrock LLM API:", e)
            return ""

    @staticmethod
    def call_bedrock_llm_new(prompt, max_tokens, temperature, top_p):
        request_model = RequestModel()
        return request_model.send_request_bedrock(
            prompt, max_tokens, temperature, top_p
        )
