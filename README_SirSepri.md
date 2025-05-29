# LearnHub - Platform Pembelajaran Modern

##  Tentang Proyek

**LearnHub** adalah platform pembelajaran online berbasis web yang dibangun menggunakan **Flask** dengan arsitektur **MVC**. Terinspirasi dari **Khan Academy**, platform ini dirancang dengan tampilan modern dan fitur lengkap untuk siswa, guru, dan admin.

## Fitur Utama

### Untuk Siswa:
- Login & Register yang aman
- Eksplorasi dan pendaftaran kursus
- Pelacakan progres dan riwayat belajar
- Dashboard pembelajaran personal

### Untuk Guru:
- Dashboard khusus guru
- Manajemen kursus, materi, dan kuis
- Statistik dan analisis pembelajaran

### Untuk Admin:
- Kelola seluruh data pengguna dan konten
- Akses penuh terhadap platform

## Teknologi yang Digunakan

- **Backend**: Flask (Python)
- **Database**: SQLite / MySQL
- **Frontend**: Bootstrap 5, AOS (animasi), Font Awesome
- **Hosting**: PythonAnywhere

## Demo Online

🔗 [http://nelsenj.pythonanywhere.com](https://nelsenj.pythonanywhere.com)

### Akun Demo

- Siswa:  
  - Username: `student1`  
  - Password: `password`
- Guru:  
  - Username: `teacher1`  
  - Password: `password`
- Admin:  
  - Username: `admin2`  
  - Password: `sirsepri`

## Cara Menjalankan Secara Lokal

1. **Clone repository**

```bash
git clone https://github.com/NelsenJ/Moodle-LearnHUB.git
cd Moodle-LearnHUB
```

2. **Buat dan aktifkan virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Windows Gitbash
python -m venv veng
source venv/Scripst/activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install semua dependensi**

```bash
pip install -r requirements.txt
```

4. **Buat file konfigurasi `.env`**

Buat file `.env` di direktori utama proyek, lalu isi seperti ini:

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=isi-dengan-kunci-rahasia
```

5. **Inisialisasi database dan jalankan**

```bash
flask db upgrade
python seed.py
python run.py
```

Aplikasi akan berjalan di `http://localhost:5000`

