import logging

import requests

logger = logging.getLogger(__name__)


def test_call_local_llm(prompt, max_tokens=50, temperature=0.7, top_p=0.9):
    url = "http://localhost:1234/v1/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["text"]
    except Exception as e:
        logger.info(f"API Error: {str(e)}")
        return ""


if __name__ == "__main__":
    resp = test_call_local_llm("Test")
    logger.info(resp)
