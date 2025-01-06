FROM python:3.13-alpine

RUN apk --no-cache add ffmpeg opus

WORKDIR /bot
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "-OO", "main.py"]
