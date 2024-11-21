FROM python:3.10.10
WORKDIR /app
EXPOSE 8000

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app/scraper/chromedriver scraper/chromedriver
RUN chmod +x scraper/chromedriver/chromedriver

RUN apt-get update && apt-get install -y \
    apt-utils \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libu2f-udev \
    libvulkan1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils

COPY . .
COPY app/ /app/

RUN dpkg -i ./installer/google-chrome-stable_current_amd64.deb
RUN apt-get install -f

CMD ["python3", "app.py"]
