ARG PYTHON_VERSION=3.10.5

FROM python:${PYTHON_VERSION}-slim as base
# ENV

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel




RUN mkdir -p /app
WORKDIR /app

COPY . .

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8000

CMD uvicorn main:app --reload --port 8000 --host 0.0.0.0
