# 1. Base image with Python
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy requirements first (better caching for rebuilds)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your project files
COPY . .

# 6. Expose the port Flask runs on
EXPOSE 5000

# 7. Command to run your app
CMD ["python", "run.py"]
