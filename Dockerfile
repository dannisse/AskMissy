FROM python:3.8-alpine

COPY requirements.txt /app/req.txt

WORKDIR /app

RUN pip install -r req.txt

COPY . /app

CMD [ "python3", "main.py", "runserver", "-h", "0.0.0.0"]

EXPOSE 5000