# FIRST TIME

##

### 1. Create Postgre Data Directory

```shell
mkdir core-data
```

### 2. Create Postgre DB

```shell
.\pgsql\bin\initdb.exe -D core-data -U core -E UTF8 --locale=en_US.UTF-8
```

### 3. Running Postgre DB

```shell
.\pgsql\bin\pg_ctl.exe -D core-data -l core.logfile start
```

### 4. Test Connect

```shell
.\pgsql\bin\psql.exe -U core
```

### 5. Change Password

```sql
ALTER USER core WITH PASSWORD 'core'
```

# RUNNING POSTGRE

```shell
.\pgsql\bin\pg_ctl.exe -D core-data -l core.logfile start
```

---

# Konfigurasi & Migrasi Database PostgreSQL dengan Alembic

Dokumen ini menjelaskan cara mengatur koneksi database PostgreSQL dan menjalankan migrasi skema menggunakan Alembic di project ini.

## 1. Konfigurasi Database

- Pastikan variabel berikut sudah diatur di file `.env`:

```
DB_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/himdb
DB_MIGRATE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/himdb
```

- Pastikan PostgreSQL sudah berjalan dan database `himdb` sudah dibuat.

## 2. Struktur Alembic

- File konfigurasi: `alembic/alembic.ini`
- Script migrasi: `alembic/versions/`
- Script env: `alembic/env.py` (sudah otomatis membaca DB_MIGRATE_URL dari .env)

## 3. Membuat Migrasi Baru

Aktifkan virtual environment, lalu jalankan:

```
venv-3.10\Scripts\alembic.exe revision --autogenerate -m "init"
```

- File migrasi baru akan muncul di `alembic/versions/`.
- Edit file migrasi jika perlu.

## 4. Menjalankan Migrasi

```
venv-3.10\Scripts\alembic.exe upgrade head
```

- Ini akan membuat/memperbarui tabel di database sesuai model SQLAlchemy.

## 5. Tips

- Jika ada perubahan pada model di `app/models/`, ulangi langkah 3 dan 4.
- Untuk melihat status migrasi:
	```
	venv-3.10\Scripts\alembic.exe current
	```
- Untuk rollback:
	```
	venv-3.10\Scripts\alembic.exe downgrade -1
	```

## 6. Referensi
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/)

---
Terakhir diperbarui: 4 September 2025