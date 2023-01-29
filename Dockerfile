FROM python:3.9.16-bullseye

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

CMD ["python", "bot.py"]
