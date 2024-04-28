FROM python:3.9

RUN apt-get update && \
    apt-get -qq -y install tesseract-ocr && \
    apt-get -qq -y install libtesseract-dev

# Set the working directory
WORKDIR /app

ADD . /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
#COPY . .

# Expose the port that the Flask app runs on
EXPOSE 10000

# Set environment variables
# ...

# Run the application
CMD ["python", "gubble.py"]