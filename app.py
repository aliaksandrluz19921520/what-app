from flask import Flask, request, Response
from twilio.rest import Client as TwilioClient
from openai import OpenAI
import os
import base64

app = Flask(__name__)

# Twilio credentials из переменных окружения
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# OpenAI credentials из переменных окружения
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Извлечение данных из запроса Twilio
    incoming_msg = request.form.get('Body', '').strip()
    num_media = int(request.form.get('NumMedia', 0))

    if num_media > 0:
        # Загрузка медиа (например, изображения) с URL из Twilio
        media_url = request.form.get('MediaUrl0')
        response = requests.get(media_url)
        image_data = response.content
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Пример обработки изображения через OpenAI (доработайте по вашим нуждам)
        try:
            openai_response = openai_client.images.generate(
                model="dall-e-3",
                prompt="Analyze the image",
                image=image_base64
            )
            reply = openai_response.data[0].url  # Или другой результат анализа
        except Exception as e:
            reply = f"Error analyzing image: {str(e)}"
    else:
        reply = "No media provided. Message received: " + incoming_msg

    # Отправка ответа через Twilio
    twilio_client.messages.create(
        body=reply,
        from_='your_twilio_number',  # Замените на ваш Twilio номер
        to='recipient_number'       # Замените на номер получателя
    )

    return Response(status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)