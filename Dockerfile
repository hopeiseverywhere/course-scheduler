# Use an official lightweight Python image.
FROM python:3.10-slim
LABEL "Project" "Basic Python API Rest"
# Set the working directory to /app
WORKDIR /app

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
