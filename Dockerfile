# 1. Use an official lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application code
# This includes your 'data' folder and 'chroma_db'
COPY . .

# 5. Expose the port FastAPI runs on
EXPOSE 8000

# 6. Command to run the API
CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "8000"]i 