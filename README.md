# 🧠 VeriFeed Backend (Django REST Framework)

This repository contains the **backend** for the **VeriFeed Deepfake Detection System**.  
It provides secure **API endpoints** for authentication, user management, feedback collection, and AI-based content verification.  
Built using **Django**, **Django REST Framework**, and **MySQL**.

---

## ⚙️ Overview

The backend serves as the core of VeriFeed, responsible for:

- 🔐 **User Authentication & Authorization** (JWT-based)  
- 💬 **Feedback Management** – Store and retrieve user reviews  
- 📸 **Profile Management** – Handle user details and avatars  
- ⚙️ **Deepfake Detection Integration** – Connects to AI detection service (from frontend)  
- 🧩 **API for Vue.js Frontend** – Provides REST endpoints consumed by the VeriFeed web extension  

---

## 🧰 Technologies Used

| Component | Technology |
|------------|-------------|
| Framework | [Django 5.x](https://www.djangoproject.com/) |
| API | [Django REST Framework (DRF)](https://www.django-rest-framework.org/) |
| Database | [MySQL](https://www.mysql.com/) |
| Authentication | JWT (via `rest_framework_simplejwt`) |
| CORS | `django-cors-headers` |
| Environment | Python 3.11+ |

---

## 🛠️ Installation Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/christinaesico456/VeriFeed-Backend.git
cd VeriFeed-Backend
```

---

### 2️⃣ Create and Activate a Virtual Environment
It’s best practice to isolate dependencies.

```bash
python -m venv venv
venv\Scripts\activate
```

For macOS/Linux:
```bash
source venv/bin/activate
```

---

### 3️⃣ Install Required Packages
Install Django and dependencies:
```bash
pip install -r requirements.txt
```

If the file isn’t present, manually install the essentials:
```bash
pip install django
pip install djangorestframework
pip install django-cors-headers
pip install mysqlclient
pip install djangorestframework-simplejwt
```

---

### 4️⃣ MySQL Configuration
Make sure MySQL Server is running, and create a new database.

**Example MySQL credentials:**

| Field | Value |
|-------|--------|
| Database Name | verifeed_db |
| Username | root |
| Password | IwillliveforJesus! |

Then configure your database in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'verifeed_db',
        'USER': 'root',
        'PASSWORD': 'IwillliveforJesus!',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

### 5️⃣ Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 6️⃣ Create a Superuser
```bash
python manage.py createsuperuser
```

Then use the following credentials (already created):

| Field | Value |
|--------|--------|
| Username | verifeed |
| Password | Akoaymagaling456 |

---

### 7️⃣ Run the Development Server
```bash
python manage.py runserver
```

Server runs at:  
👉 **http://127.0.0.1:8000/**

---

### 8️⃣ API Endpoints Overview

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/accounts/register/` | POST | Register a new user |
| `/api/accounts/login/` | POST | Obtain JWT tokens |
| `/api/accounts/profile/` | GET | View logged-in user profile |
| `/api/reviews/` | GET / POST | Retrieve or submit feedback |
| `/api/token/` | POST | Generate JWT access & refresh tokens |

---

## 🧩 Environment Configuration

If using environment variables, create a `.env` file in your backend root:
```bash
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=*
DATABASE_NAME=verifeed_db
DATABASE_USER=root
DATABASE_PASSWORD=IwillliveforJesus!
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

---

## 🔗 Frontend Integration

Your Vue.js Frontend communicates with this backend through the following base URL:
```bash
http://127.0.0.1:8000/api/
```

Make sure your CORS settings allow frontend requests.  
Add this to `settings.py`:
```python
INSTALLED_APPS = [
    'corsheaders',
    'rest_framework',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOW_ALL_ORIGINS = True
```

---

## 📦 Dependencies Summary
```bash
Django==5.x
djangorestframework==3.x
django-cors-headers==4.x
mysqlclient==2.x
djangorestframework-simplejwt==5.x
```

---

## 🧪 Testing the API

You can test API endpoints using **Postman** or **cURL**.  
Base URL:
```
http://127.0.0.1:8000/api/
```

Example login test:
```bash
POST /api/accounts/login/
{
  "username": "verifeed",
  "password": "Akoaymagaling456"
}
```

---

## 🧑‍💻 Author

Developed by **GANcd VeriF**  
Academic Research Project – *De La Salle University – Dasmariñas*

---

## 📜 License

This project is intended for **academic and research use only**.  
Do not redistribute or commercialize without permission from the authors.
