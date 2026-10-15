# অফিসিয়াল পাইথন ইমেজ ব্যবহার করা হচ্ছে
FROM python:3.12-slim

# কাজের ডিরেক্টরি সেট করা
WORKDIR /app

# সিস্টেমের প্রয়োজনীয় টুলস ইনস্টল করা
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt কপি করা এবং লাইব্রেরি ইনস্টল করা
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# প্রজেক্টের বাকি ফাইলগুলো কপি করা
COPY . .

# বট চালু করার কমান্ড
CMD ["python", "app.py"]
