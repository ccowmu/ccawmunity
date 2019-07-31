FROM python:alpine3.8

WORKDIR /ccaw

ADD chatbot/ /ccaw
ADD start.sh /ccaw

RUN pip install -r requirements.txt

CMD ["python", "./chat.py"]
