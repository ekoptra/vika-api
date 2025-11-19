# Vika API - Voice Navigation SDK

API backend untuk voice-based navigation menggunakan FastAPI + Socket.IO.

## Tentang Project

Vika adalah SDK API yang memungkinkan aplikasi mobile untuk mengimplementasikan navigasi berbasis suara. Pengguna dapat berbicara untuk navigasi ke screen tertentu dalam aplikasi, dan sistem akan memproses audio, memahami intent, dan memberikan instruksi navigasi yang tepat.

### Cara Kerja:

1. **Inisialisasi**: Client aplikasi melakukan autentikasi dengan API key dan signature HMAC-SHA256
2. **Registrasi Screen**: Client mendaftarkan daftar screen yang tersedia beserta deep link dan keywords
3. **Voice Input**: User berbicara untuk request navigasi (misal: "Buka halaman profile")
4. **Processing**: Audio diproses secara asynchronous, sistem mencocokkan dengan screen yang terdaftar
5. **Real-time Response**: Client menerima notifikasi hasil via Socket.IO dengan informasi screen tujuan dan deep link

### Key Features:

- **Signature-based Authentication**: Keamanan dengan HMAC-SHA256 signature verification
- **Session Management**: Bearer token untuk autentikasi request selanjutnya
- **Async Audio Processing**: Upload audio mendapat response immediate, processing dilakukan di background
- **Real-time Notification**: Socket.IO untuk notifikasi hasil processing
- **Flexible Screen Management**: Client dapat update screen list kapan saja

## Setup Lokal (Development)

### 1. Prerequisites

- Python 3.12+
- Poetry
- PostgreSQL database

### 2. Install Dependencies

```bash
# Install Poetry jika belum ada
pip install poetry

# Install project dependencies
poetry install
```

### 3. Configure Environment

Buat file `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/vika_db
UPLOAD_DIR=uploads/audio
```

### 4. Setup Database

```bash
# Run migrations
poetry run prisma db push
```

### 5. Run Server

```bash
# Development mode dengan auto-reload
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di http://localhost:8000

- **API Docs**: http://localhost:8000/docs
- **Socket.IO**: http://localhost:8000/socket.io
- **Socket.IO Test Page**: http://localhost:8000/test/socket

## Setup with Docker

### 1. Configure Environment

Buat file `.env`:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
UPLOAD_DIR=uploads/audio
```

### 2. Build & Run

```bash
# Build image
docker-compose build

# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### 3. Run Migrations

```bash
docker-compose exec app alembic upgrade head
```

## Endpoints

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Socket.IO**: http://localhost:8000/socket.io
- **Socket.IO Test Page**: http://localhost:8000/test/socket

## Main Features

- **POST /auth/initialize** - Initialize session dengan API key
- **POST /screen/** - Update registered screens
- **POST /conversation/** - Upload audio untuk voice navigation
- **Socket.IO** - Real-time notification untuk hasil processing

## Tech Stack

- FastAPI
- Socket.IO
- PostgreSQL
- SQLAlchemy + Alembic
- Python 3.12
