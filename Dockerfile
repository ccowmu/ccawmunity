FROM python:alpine3.8

ADD chatbot/ .

CMD ["python", "chatbot/chat.py"]