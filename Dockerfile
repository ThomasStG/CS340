FROM python:3.11-slim

WORKDIR .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data ./data
COPY docs ./docs
COPY logs ./logs
COPY src ./src

EXPOSE 3000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "src.app:app"]
