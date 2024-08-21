# 1. Use an official Python runtime as a parent image
FROM python:3.9-slim

# 3. Set the working directory in the container
WORKDIR /app

# 4. Copy the requirements file
COPY requirements.txt .

# 5. Install Python dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Expose the port that the application will run on
EXPOSE 8080

# 8. Set environment variables (if needed)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# 9. Run the application
CMD ["flask", "run"]

