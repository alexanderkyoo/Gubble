FROM python:3.9

# Install Tesseract-OCR
RUN apt-get update && \
    apt-get -qq -y install tesseract-ocr libtesseract-dev

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the port the Flask app runs on
EXPOSE 10000

# Set environment variables (if needed)
# ENV FLASK_ENV=production

# Run the Flask application
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "gubble.app:app"]