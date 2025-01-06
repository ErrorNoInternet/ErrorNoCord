FROM python:3.13.1-alpine

WORKDIR /bot
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
