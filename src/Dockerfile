# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5001  
EXPOSE 4840  

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x start.sh

CMD ["./start.sh"]
