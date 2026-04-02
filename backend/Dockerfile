FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for tiktoken (needs Rust)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directories
RUN mkdir -p data/daily data/weekly

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
