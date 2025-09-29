FROM python:3.12-slim

WORKDIR /backend

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /backend
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /backend

CMD ["sh", "-c", "export PYTHONPATH=/backend && cd /backend/app && alembic upgrade head && cd /backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
