from flask import Flask, request, Response
from twilio.rest import Client as TwilioClient
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
import os
import requests
import base64

app = Flask(__name__)

# Twilio credentials из переменных окружения
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# OpenAI API key из переменных окружения
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

@app.route('/webhook', methods=['POST'])
def webhook():
    # Получаем текст сообщения и количество медиафайлов
    incoming_msg = request.form.get('Body', '').strip()
    num_media = int(request.form.get('NumMedia', 0))
    
    if num_media > 0:
        # Обработка фото
        media_url = request.form.get('MediaUrl0')
        response = requests.get(media_url)
        image_data = response.content
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Промпт для анализа фото с вариантами ответа
        prompt = "На фото изображен вопрос с вариантами ответов. Пожалуйста, проанализируйте изображение, прочитайте вопрос и варианты, и выберите наиболее правильный ответ. Укажите букву или номер правильного варианта."
        
        # Запрос к OpenAI (адаптируйте под реальный API)
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Замените на актуальную модель (например, gpt-4o для мультимодальности)
            messages=[
                {"role": "user", "content": prompt},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}]}
            ]
        )
        reply = response.choices[0].message.content.strip()
    else:
        # Обработка текста
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        reply = response.choices[0].message.content.strip()
    
    # Создаем TwiML для отправки ответа в WhatsApp
    twiml = MessagingResponse()
    twiml.message(reply)
    return Response(str(twiml), mimetype='application/xml')

if __name__ == '__main__':
    # Локальный запуск с учетом порта от окружения
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)