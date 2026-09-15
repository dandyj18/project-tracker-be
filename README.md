# Project Tracker - Backend API

Rest API backend untuk aplikasi Project Tracker, dibangun dengan Python Flask, Flask-SQLAlchemy, dan PostgreSQL.

## 🚀 Fitur Utama

1. **Management Project & Task**
   - CRUD Project dengan perhitungan persentase penyelesaian otomatis (`completion_progress`) berbasis bobot task status `Done`.
   - CRUD Task & Subtask hierarkis (dukungan nested subtasks & bobot task).

2. **Validasi Dependensi Task (Instruksi Tambahan #1)**
   - Task tidak dapat diubah statusnya menjadi `Done` jika task dependensinya belum `Done`.
   - Deteksi siklus dependensi sirkular (Circular Dependency Prevention) menggunakan algoritma DFS graph traversal.

3. **Validasi Dependensi Project (Instruksi Tambahan #2)**
   - Project tidak dapat diubah menjadi `In Progress` atau `Done` jika prasyarat project belum `Done`.
   - Otomatis memvalidasi rantai dependensi antar project.

4. **Hierarchical Subtask Filtering & Search (Instruksi Tambahan #3)**
   - Pencarian dan filter status berlaku secara rekursif hingga ke level subtask.
   - Menjaga konsistensi konteks hierarki parent-child.

5. **Project Schedule Non-Intersecting Validator (Instruksi Tambahan #4)**
   - Validasi jadwal rentang tanggal `[start_date, end_date]` project tidak boleh saling tumpang tindih (overlapping).
   - Memberikan pesan error spesifik jika terjadi bentrok jadwal.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Framework**: Flask
- **ORM**: Flask-SQLAlchemy
- **Database**: PostgreSQL (Fallback ke SQLite untuk testing lokal tanpa konfigurasi DB)
- **Migration & Seeding**: Script seeding data bawaan (`seed.py`)

---

## ⚙️ Cara Menjalankan Backend

### 1. Prasyarat & Instalasi

```bash
# Masuk ke direktori backend
cd backend

# Buat virtual environment (opsional)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi Environment (Opsional)

Buat file `.env` berdasarkan `.env.example`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=project_tracker
FLASK_ENV=development
PORT=5000
```

*Catatan: Jika PostgreSQL tidak tersedia, sistem akan otomatis fallback menggunakan database SQLite lokal (`project_tracker.db`).*

### 3. Data Seeding & Jalankan Server

```bash
# Seed initial sample data
python seed.py

# Jalankan server API
python app.py
```

Server backend akan berjalan di `http://localhost:5000`.

---

## 📡 Endpoints API

### Projects
- `GET /api/projects` - List semua project (dengan progress & status dependensi)
- `GET /api/projects/<id>` - Detail project
- `POST /api/projects` - Tambah project baru (dengan validasi non-intersecting schedule & dependensi)
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Hapus project

### Tasks
- `GET /api/projects/<project_id>/tasks` - List task & subtask dalam project
- `POST /api/tasks` - Tambah task/subtask (dengan validasi dependensi sirkular)
- `PUT /api/tasks/<id>` - Update status/bobot/detail task (dengan validasi status dependensi)
- `DELETE /api/tasks/<id>` - Hapus task
