from flask import Flask, request
import requests
import os
import base64

app = Flask(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

@app.route('/webhook', methods=['POST'])
def webhook():
    media_url = request.form.get('MediaUrl0')
    if not media_url:
        return "No media found", 400

    # Скачиваем изображение с Twilio
    auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    media_response = requests.get(media_url, auth=auth)
    image_data = base64.b64encode(media_response.content).decode('utf-8')

    # Отправляем изображение в GPT-4o
    gpt_response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Ты эксперт по анализу изображений."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Проанализируй это изображение."},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                    ]
                }
            ]
        }
    ).json()

    reply = gpt_response["choices"][0]["message"]["content"]
    return f"<Response><Message>{reply}</Message></Response>", 200, {'Content-Type': 'application/xml'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)