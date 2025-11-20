# 🐞 Bug Tracking Optimization Tool  
### Python · MongoDB · Streamlit

The **Bug Tracking Optimization Tool** is a lightweight yet powerful system designed to streamline the process of reporting, tracking, testing, and resolving bugs across software modules.  
It provides both a **Command-Line Interface (CLI)** and an intuitive **Streamlit GUI Dashboard**, backed by a **MongoDB NoSQL database**.

---

## 🚀 Features

### ✔ Core Functionalities
- Create structured bug reports  
- Add automated or manual test logs  
- Update bug statuses (Open → In-progress → Resolved → Closed)  
- View, filter, and search bugs  
- Store all bug data in MongoDB  
- Track Git commit version for each bug  

### ✔ User Interfaces
- **CLI Tool:**  
  Can create bugs, update them, add logs, etc.

- **Streamlit GUI Dashboard:**  
  Easy-to-use browser interface with forms, filters, and expandable bug cards.

---

## 🧩 Technology Stack

| Component | Technology |
|----------|------------|
| Backend  | Python |
| Database | MongoDB |
| Frontend | Streamlit |
| Version Control | Git |
| Libraries | pymongo, streamlit, bson |

---

## 📁 Project Structure

Bug Tracking Tool/
│── bug_tracker.py # CLI tool
│── app.py # Streamlit Dashboard
│── README.md # Documentation
│── requirements.txt # (Optional) All dependencies

---

## 🔧 Installation Guide

### 1. Install Python Dependencies  
Use Python’s module runner:

```bash
py -m pip install pymongo streamlit
2. Ensure MongoDB is Running

If using local MongoDB:
▶ Running the CLI Tool
🌱 Create Bug
Architecture Overview
1️⃣ Input Layer

CLI commands

Streamlit UI forms

2️⃣ Processing Layer

Python functions for CRUD

Git commit fetch

Data validation

3️⃣ Database Layer (MongoDB)

Stores:

Bugs

Logs

Status updates

4️⃣ Output Layer

Terminal output

Streamlit dashboard visualization

❤️ Advantages

Better debugging workflow

Centralized bug history

Easy log and status management

UI + CLI flexibility

Suitable for teams and individuals

📌 Future Enhancements

User authentication

Screenshot/file uploads

Bug assignment to developers

Email/SMS notifications

Analytics dashboard for trends

👤 Author

Aditi Gupta
Final Year B.Tech Computer Science