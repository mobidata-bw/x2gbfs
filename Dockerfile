FROM python:3-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY x2gbfs/ ./x2gbfs/
COPY config/ ./config/

ENTRYPOINT [ "python", "-m", "x2gbfs.x2gbfs" ]
