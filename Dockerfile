# Dockerfile
# Use uma imagem base com Python
FROM python:3.9-slim

# Instale as dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Baixe e instale o Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Baixe e instale o ChromeDriver
RUN wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip --version && \
    python --version

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "source/modules/frontend/app.py"]