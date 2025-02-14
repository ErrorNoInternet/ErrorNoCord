FROM python:3.13-alpine

RUN apk --no-cache add ffmpeg gcc linux-headers musl-dev opus python3-dev

WORKDIR /bot
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
