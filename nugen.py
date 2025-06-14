import requests
import json

def fact_check(claim):
    API_URL = "https://api.nugen.in/api/v3/agents/healthbu-c978gxqs/run/?stream=false"
    API_KEY = "nugen-AHjOfMD5vtpRpqPsR0At-g"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": claim
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print("Agent Response:\n")
        print(result.get("response", "No response found."))
        if result.get("response") == "**(No recent medical claims made)**":
            return None
        return result.get("response")
    else:
        print(f"Request failed: {response.status_code}")
        print(response.text)