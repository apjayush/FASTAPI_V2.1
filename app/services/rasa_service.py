import httpx

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"  
# Change if running Rasa on different URL

async def send_to_rasa(sender: str, message: str):
    payload = {
        "sender": sender,
        "message": message
    }

    print(f"Sending to Rasa: {payload}")  # for debugging

    async with httpx.AsyncClient() as client:
        response = await client.post(RASA_URL, json=payload)
        return response.json()
