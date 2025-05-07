import requests
import os

HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

def describe_image(image_url):
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": image_url}
        )
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "No description.")
        return f"[Vision Error {response.status_code}]"
    except Exception as e:
        return f"[Vision failed: {str(e)}]"
