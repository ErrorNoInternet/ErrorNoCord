FROM python:3.13.1-alpine

RUN apk --no-cache add ffmpeg

WORKDIR /bot
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "-OO", "main.py"]
