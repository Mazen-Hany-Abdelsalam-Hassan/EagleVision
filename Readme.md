# 🍕 Scooper Violation Detection System – Pizza Store Monitoring

A microservices-based computer vision system for monitoring hygiene compliance in pizza stores.  
Detects whether workers use a scooper when handling ingredients, logs violations, and streams annotated video in real-time.

---

## 📌 Project Overview

This system:
- Captures frames from live video streams.
- Detects when ingredients are handled **without** a scooper inside defined Regions of Interest (ROIs).
- Logs violations and streams annotated video through a FastAPI web interface.

Built with:
- Python 3.12.3
- PyTorch & YOLO
- Celery & RabbitMQ
- FastAPI
- Docker Compose

---

## 📂 Project Structure

```plaintext
EagleVision/
├── Docker/
│   └── docker-compose.yml
├── src/
│   ├── AI_Service/
│   ├── assets/
│   ├── Controllers/
│   ├── Helper/
│   ├── Models/
│   ├── routes/
│   ├── Workers/
│   │   ├── VideoToFrames.py
│   │   └── FrameReader.py
│   └── YOLO_Model/
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Setup & Installation

✅ Make sure you have Conda, Python 3.12.3, Docker, and Docker Compose installed.

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/EagleVision.git
cd EagleVision
```

### 2️⃣ Create and activate Conda virtual environment (Python 3.12.3)

```bash
conda create -n eaglevision python=3.12.3
conda activate eaglevision
```

### 3️⃣ Install Python dependencies

Install PyTorch (CPU version):

```bash
pip install torch==2.7.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

Install other project requirements:

```bash
cd src
pip install -r requirements.txt
```

### 4️⃣ Start RabbitMQ with Docker Compose

```bash
cd Docker
docker compose up -d
```

RabbitMQ management console: http://localhost:15672

---

## ⚙️ Running the Services

Open separate terminals or use a process manager in production.

### 🎞 VideoToFrame Service
Captures frames from video streams.

```bash
cd src
celery -A Workers.VideoToFrames worker --loglevel=info --pool=eventlet --concurrency=2
```

### 🧠 FrameReader Service
Runs scooper violation detection.

```bash
cd src
celery -A Workers.FrameReader worker --loglevel=info --pool=eventlet --concurrency=2
```

### 🌐 FastAPI Web App
Serves the web interface and API.

```bash
cd src
uvicorn main:app --reload
```

Open in browser: http://127.0.0.1:8000

---

https://github.com/user-attachments/assets/c0832353-8f98-4718-980f-260970d84d94

## 🛠 Features

✅ Real-time scooper violation detection  
✅ Live streaming of annotated video  
✅ Microservices & distributed task queue  
