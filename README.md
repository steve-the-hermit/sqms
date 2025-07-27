

# 🏥 Smart Queue Management System (SQMS2)

SQMS2 is a Flask-based web application designed to streamline and automate patient check-ins, doctor assignments, and service logging in a clinical or hospital setting. The system supports admin and doctor roles, real-time queue simulation, and advanced export features.


## 🚀 Features

- ✅ Patient check-in with visit category and auto-assignment to the least busy doctor
- 🧾 Instant receipt generation showing assigned doctor and estimated wait
- 🧠 Optional simulation of real-time check-ins and patient serving
- 📊 Admin dashboard with:
  - Real-time patient queue
  - Filters by doctor and status
  - Manual patient serving
- 🔐 Admin login with session protection
- 👨‍⚕️ Doctor login and doctor-specific dashboard to serve only their assigned patients
- 🌙 Dark mode toggle for better UX
- 📂 Logs of actions with export options (CSV, Excel, PDF)
- 📈 Real-time queue stats and dynamic updates
- 🧾 Printable receipts


## 🧰 Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Frontend:** HTML5, CSS3, JavaScript (vanilla)
- **Database:** MySQL
- **Exports:** Pandas, ReportLab, xlsxwriter
- **PDF/Excel/CSV Export:** Enabled with formatted file output



## 📁 Project Structure



sqms2/
│
├── app/
│   ├── **init**.py
│   ├── routes.py
│   ├── models.py
│   ├── templates/
│   │   ├── home.html
│   │   ├── checkin.html
│   │   ├── dashboard.html
│   │   ├── doctor\_dashboard.html
│   │   ├── logs.html
│   │   └── login.html
│   └── static/
│       ├── styles.css
│       └── scripts.js
│
├── config.py
├── main.py
├── requirements.txt
└── README.md

`



## 🛠️ Setup Instructions

### 1. Clone the Repository
bash
git clone https://github.com/steve-the-hermit/sqms2.git
cd sqms2
`

### 2. Create Virtual Environment

bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate


### 3. Install Dependencies

bash
pip install -r requirements.txt


### 4. Set Up Database

* Ensure MySQL is running.
* Create a new database (e.g., `sqms2`).
* Update your `config.py` with your MySQL credentials.
* Initialize migrations and apply them:

bash
flask db init
flask db migrate -m "Initial schema"
flask db upgrade


### 5. Run the Application

bash
python main.py




## 🔐 Default Admin Login

* **Username:** `admin`
* **Password:** `admin` *(change this in production)*



## 📤 Export Formats

* **CSV:** `/export/csv`
* **Excel:** `/export/excel`
* **PDF:** `/export/pdf`





## 📌 Pending Quality-of-Life adjustments

* ✅ Finalize print receipt UI
* ✅ Doctor-specific stats and login
* ⬜ Notification support (email/SMS)
* ⬜ Queue prediction with ML model (future scope)



## 👨‍💻 Developed by

* **Steve Macharia**
  [GitHub](https://github.com/steve-the-hermit) | [LinkedIn](https://linkedin.com/in/your-linkedin)



## 📄 License

MIT License. Free to use and modify.Please contact if you intend to use this product.

