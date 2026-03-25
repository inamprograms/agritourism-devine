FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
CMD ["sh", "-c", "gunicorn --workers=1 --threads=2 --bind 0.0.0.0:$PORT main:app"]