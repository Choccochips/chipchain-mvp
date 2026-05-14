FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

EXPOSE 5000

# for mac commands to run them 
CMD ["python3", "-m", "api.app"]