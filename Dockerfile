FROM python:3.10.4-alpine3.15

WORKDIR /usr/scr/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python3", "./main.py"]