from flask import Flask, request, Response
from twilio.rest import Client as TwilioClient
from openai import OpenAI
import os
import base64
import requests

# Инициализация приложения Flask
app = Flask(__name__)

# Учетные данные из переменных окружения (настроить в Railway)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')  # Ваш номер Twilio
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Инициализация клиентов
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Обработчик вебхука для обработки входящих сообщений
@app.route('/webhook', methods=['POST'])
def webhook():
    # Извлечение данных из запроса Twilio
    incoming_msg = request.form.get('Body', '').strip()
    num_media = int(request.form.get('NumMedia', 0))
    from_number = request.form.get('From', '')  # Номер отправителя

    # Если есть медиа (например, изображение)
    if num_media > 0:
        media_url = request.form.get('MediaUrl0')  # URL первого медиафайла
        response = requests.get(media_url)
        image_data = response.content
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Анализ изображения через OpenAI
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Опиши это изображение."},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Ошибка анализа изображения: {str(e)}"
    else:
        # Анализ текстового сообщения через OpenAI
        reply = f"Вы отправили: {incoming_msg}. Анализ: "
        try:
            openai_response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": incoming_msg}],
                max_tokens=100
            )
            reply += openai_response.choices[0].message.content
        except Exception as e:
            reply += f"Ошибка OpenAI: {str(e)}"

    # Отправка ответа через Twilio
    try:
        twilio_client.messages.create(
            body=reply,
            from_=TWILIO_PHONE_NUMBER,
            to=from_number
        )
    except Exception as e:
        return Response(f"Ошибка отправки сообщения: {str(e)}", status=500)

    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
