# Use a base image
FROM python:3.11-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libx11-dev \
    libxkbfile-dev \
    libsecret-1-dev \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libxss1 \
    libasound2

# Ensure the /app directory exists, then create .wdm inside it
RUN mkdir -p /app && if [ ! -d "/app/.wdm" ]; then \
        echo "Creating .wdm directory"; \
        mkdir /app/.wdm; \
    fi

# Set the working directory
WORKDIR /app

# Copy the necessary files
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the entry point script
ENTRYPOINT ["bash", "entry.sh"]
