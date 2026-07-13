FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN python -m pip install --no-cache-dir -e .

CMD ["python", "-m", "mathcode_mini.cli", "demo"]
