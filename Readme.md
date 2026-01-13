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

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd "Bug Tracking Tool"
```

### 2. Install Dependencies
It is recommended to use a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Configuration
By default, the app looks for a local MongoDB at `mongodb://localhost:27017/`.  
To use a different database (like MongoDB Atlas), set the `MONGO_URI` environment variable:
```bash
# Windows
set MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
# Linux/Mac
export MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
```

---

## 🚀 Deployment

### Streamlit Community Cloud
1. Push your code to GitHub.
2. Connect your repository to [Streamlit Cloud](https://share.streamlit.io/).
3. In the app settings on Streamlit Cloud, go to **Secrets** and add:
   ```toml
   MONGO_URI = "your_mongodb_atlas_connection_string"
   ```

---

## ❤️ Advantages
- **Streamlined Workflow**: Easily track bug lifecycle from report to resolution.
- **Dual Interface**: Use CLI for quick updates or the Dashboard for a visual overview.
- **Cloud Ready**: Configured for easy deployment with environment variable support.

---

## 👤 Author
**Aditi Gupta**  
Final Year B.Tech Computer Science