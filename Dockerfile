# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Update package list and install vim non-interactively
RUN apt update -y && apt install -y vim

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files to the container
COPY . .

# Expose the port that the app will run on
EXPOSE 3003

# Run migrations and start the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3003", "portfoliobackend.wsgi:application"]
 