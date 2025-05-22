## 📘 LearnHub – A Modern Learning Platform

**LearnHub** is a modern web-based learning platform built with **Flask** using the **MVC (Model-View-Controller)** architecture. Inspired by **Khan Academy**, it focuses on user experience and a clean, responsive design to support students, teachers, and administrators.

## Readme khusus Sir Sepri

> 🇮🇩 readme untuk sir sepri [Click here for README_SirSepri.md](./README_SirSepri.md)

## 🌐 Live Demo & Repository

* **Live Site**: [http://seiryu.pythonanywhere.com](http://seiryu.pythonanywhere.com)
* **Source Code**: [GitHub Repository](https://github.com/NelsenJ/Moodle-LearnHUB)

## 🌟 Key Features

### For Students

* Beautiful, responsive UI with animations
* Secure login and registration
* Browse and enroll in courses
* Track learning progress and history
* Personalized dashboard

### For Teachers

* Teacher-specific dashboard
* Course and content management
* Learning analytics and progress tracking
* Integrated grading system

### For Admins

* Full access to manage users and content
* Control panel for platform management

## 🛠️ Tech Stack

* **Backend**: Flask (Python)
* **Database**: SQLite / MySQL
* **Frontend**:

  * Bootstrap 5
  * AOS (Animate on Scroll)
  * Font Awesome
* **Deployment**: PythonAnywhere

## 🚀 Getting Started Locally

### Prerequisites

* Python 3.8+
* Git
* pip
* Virtual environment (venv)

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/NelsenJ/Moodle-LearnHUB.git
cd Moodle-LearnHUB
```

2. **Create and activate a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create a `.env` file** in the root directory:

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

5. **Initialize the database and run the app**

```bash
flask db upgrade
python seed.py
python run.py
```

The app will be available at `http://localhost:5000`

## 📝 License

This project is licensed under the MIT License – see the LICENSE file for details.


