import os
import requests
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from twilio.rest import Client
import openai

load_dotenv()

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# OpenAI config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    from_number = form.get("From")
    media_url = form.get("MediaUrl0")
    
    if not media_url:
        raise HTTPException(status_code=400, detail="No image found in the message.")

    # Отправляем фото в GPT-4o
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты помощник, который решает тестовые вопросы с фото."},
            {"role": "user", "content": [
                {"type": "text", "text": "На фото тестовый вопрос с вариантами ответов. Выбери правильный."},
                {"type": "image_url", "image_url": {"url": media_url}}
            ]}
        ]
    )
    answer = response['choices'][0]['message']['content']

    # Отправляем ответ пользователю в WhatsApp
    twilio_client.messages.create(
        from_=TWILIO_PHONE_NUMBER,
        to=from_number,
        body=f"Правильный ответ: {answer}"
    )

    return {"status": "success", "answer": answer}