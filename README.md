# LearnHub - Platform Pembelajaran Modern

LearnHub adalah platform pembelajaran modern yang dibangun menggunakan Flask, mengikuti pola MVC (Model-View-Controller). Platform ini menyediakan pengalaman belajar yang mirip dengan Khan Academy dengan fokus pada pengalaman pengguna dan desain modern.

## 🌐 Link Penting

- **Website**: [LearnHub](http://seiryu.pythonanywhere.com)
- **Repository**: [GitHub LearnHub](https://github.com/NelsenJ/Moodle-LearnHUB)

## 🌟 Fitur Utama

### Untuk Siswa
- Antarmuka yang indah dan responsif dengan animasi modern
- Sistem autentikasi (login/register) yang aman
- Pencarian dan filter kursus yang mudah digunakan
- Sistem pendaftaran kursus
- Pelacakan kemajuan belajar
- Dashboard modern untuk memantau pembelajaran
- Riwayat pembelajaran yang terorganisir

### Untuk Pengajar
- Dashboard khusus pengajar
- Manajemen kursus yang mudah
- Statistik dan analitik pembelajaran
- Sistem penilaian terintegrasi

## 🛠️ Teknologi yang Digunakan

- **Backend**: Flask (Framework Python)
- **Database**: SQLite/MySQL
- **Frontend**: 
  - Bootstrap 5 (Framework CSS)
  - AOS (Animate On Scroll library)
  - Font Awesome (Ikon)
- **Deployment**: PythonAnywhere

## 🚀 Cara Menggunakan Website

Website ini sudah di-deploy dan dapat diakses melalui:
- URL: [http://seiryu.pythonanywhere.com](http://seiryu.pythonanywhere.com)

### Cara Mengakses Website
1. Buka browser (Chrome, Firefox, Safari, dll)
2. Kunjungi [http://seiryu.pythonanywhere.com](http://seiryu.pythonanywhere.com)
3. Anda dapat langsung menjelajahi kursus yang tersedia
4. Untuk mengakses fitur lengkap, silakan daftar atau login

### Akun Demo
Untuk mencoba fitur-fitur website, Anda dapat menggunakan akun demo berikut:

**Siswa:**
- Email: student@example.com
- Password: password123

**Pengajar:**
- Email: teacher@example.com
- Password: password123

## 💻 Cara Mengembangkan Website Ini

### Prasyarat
- Python 3.8 atau lebih baru
- Git
- pip (Python package manager)
- Virtual environment (venv)

### Langkah-langkah Pengembangan

1. **Clone Repository**
```bash
git clone https://github.com/NelsenJ/Moodle-LearnHUB.git
cd Moodle-LearnHUB
```

2. **Buat dan Aktifkan Virtual Environment**
```bash
# Untuk Windows
python -m venv venv
venv\Scripts\activate

# Untuk Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Konfigurasi Environment**
Buat file `.env` di direktori utama dengan isi:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

5. **Inisialisasi Database**
```bash
flask db upgrade
python seed.py
```

6. **Jalankan Aplikasi**
```bash
python run.py
```
Aplikasi akan berjalan di `http://localhost:5000`

## 📁 Struktur Proyek

```
learnhub/
├── app/                    # Direktori utama aplikasi
│   ├── __init__.py        # Inisialisasi aplikasi Flask
│   ├── models.py          # Model database
│   ├── auth/              # Modul autentikasi
│   │   ├── __init__.py
│   │   ├── forms.py      # Form autentikasi
│   │   └── routes.py     # Route autentikasi
│   ├── main/             # Modul utama
│   │   ├── __init__.py
│   │   └── routes.py     # Route utama
│   ├── courses/          # Modul kursus
│   │   ├── __init__.py
│   │   └── routes.py     # Route kursus
│   └── templates/        # Template HTML
│       ├── base.html     # Template dasar
│       ├── index.html    # Halaman utama
│       ├── explore.html  # Halaman eksplorasi
│       └── auth/         # Template autentikasi
├── config.py             # Konfigurasi aplikasi
├── requirements.txt      # Daftar dependensi
└── run.py               # File untuk menjalankan aplikasi
```

## 🤝 Berkontribusi

Kami sangat menerima kontribusi dari siapa saja! Berikut cara berkontribusi:

1. Fork repository ini
2. Buat branch baru (`git checkout -b fitur-baru`)
3. Commit perubahan Anda (`git commit -m 'Menambahkan fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

## 📝 Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file LICENSE untuk detail lebih lanjut.

## 📞 Kontak & Dukungan

Jika Anda memiliki pertanyaan atau membutuhkan bantuan, silakan:
- Buat issue di [GitHub repository](https://github.com/NelsenJ/Moodle-LearnHUB/issues)
- Hubungi pengembang melalui [GitHub profile](https://github.com/NelsenJ)

---

Dibuat dengan ❤️ oleh [NelsenJ](https://github.com/NelsenJ) 