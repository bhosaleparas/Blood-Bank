# 🩸 Blood Bank Management System

This is a Django-based web application that manages blood donations and requests between donors, hospitals, and receivers. The system provides functionalities for admins to manage users, monitor blood stock, and handle blood request approvals.

---

## 🔧 Features

### 👨‍⚕️ Admin Panel
- Login for admin
- View dashboard with total counts (donors, receivers, hospitals, blood stock)
- Manage blood stock (add, update, delete)
- Handle blood requests (approve/reject)
- View and manage registered donors and receivers
- Manage hospital records
- System alerts for low stock levels
- Download reports

### 🩸 Donor Module
- Register/login
- Submit blood donation form
- View donation history

### 🧍‍♀️ Receiver Module
- Register/login
- Request blood (select group, quantity, hospital)
- View status of blood request

---

## ⚙️ Tech Stack

- **Backend**: Django 4.x
- **Frontend**: HTML5, CSS3, Bootstrap
- **Database**: SQLite (default) or MySQL
- **Authentication**: Django auth system
- **Messages**: Django messages framework

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/bhosaleparas/Blood-Bank.git
cd bloodbank

```
### 2.Create a Virtual Environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate

```
### 3.Install Dependencies
```bash
pip install -r requirements.txt

```
### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate

```
### 5. Run the Server
```bash
python manage.py runserver



