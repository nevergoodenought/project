FROM python:3.11-slim
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y netcat-openbsd

     
COPY . .

RUN chmod +x ./entrypoint.sh

EXPOSE 5003

ENTRYPOINT ["./entrypoint.sh"]
   
