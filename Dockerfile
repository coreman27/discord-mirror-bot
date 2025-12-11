FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver that matches Chrome version
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1) && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip || \
    (wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR_VERSION" -O /tmp/LATEST && \
     wget -q "https://chromedriver.storage.googleapis.com/$(cat /tmp/LATEST)/chromedriver_linux64.zip" -O /tmp/chromedriver.zip) && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    # move the extracted binary to /usr/local/bin where it will be found
    if [ -f /tmp/chromedriver-linux64/chromedriver ]; then \
        mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    elif [ -f /tmp/chromedriver ]; then \
        mv /tmp/chromedriver /usr/local/bin/chromedriver; \
    else \
        echo "chromedriver binary not found after unzip"; exit 1; \
    fi && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 /tmp/LATEST

# Set environment variables for Chrome and ChromeDriver
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER=/usr/local/bin/chromedriver

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
