FROM python:3.11-bullseye
WORKDIR /
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT /usr/local/bin/python3 /src/csv-to-postgres.py