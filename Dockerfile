FROM python:alpine3.8

WORKDIR /ccaw

ADD chatbot/requirements.txt /ccaw
RUN apk update && apk add gcc libc-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ADD chatbot/ /ccaw

CMD ["python3", "./chat.py"]
