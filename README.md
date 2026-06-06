# GuidX - AI-Powered Chatbot for College Enquiry System

An intelligent chatbot system designed to assist students with college-related inquiries using machine learning and natural language processing.

## 🎯 Features

- **AI-Powered Responses**: Uses trained ML models to provide intelligent answers to college enquiries
- **Multiple Course Support**: Dedicated models for Arts & Science, Engineering, and Medical programs
- **User Authentication**: Secure login and signup system
- **Chat History**: Track and review past conversations
- **Student Profiles**: Manage student information and course preferences
- **Search History**: Keep records of search queries for personalized recommendations
- **Smart Search**: Intelligent search functionality to find relevant information quickly
- **Voice Support**: Voice-enabled interactions for better accessibility
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Django 3.2+
- SQLite3
- Virtual Environment (recommended)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/pragadeesh1209/GuidX.git
cd GuidX
```

### 2. Create and Activate Virtual Environment
```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
cd college_chatbot
pip install -r requirements.txt
```

### 4. Configure Database
```bash
# Navigate to project directory
cd college_chatbot

# Apply migrations
python manage.py migrate
```

### 5. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser to access the chatbot.

## 📁 Project Structure

```
college_chatbot/
├── manage.py                 # Django management script
├── requirements.txt          # Project dependencies
├── db.sqlite3               # Database file
├── college_chatbot/         # Main Django project
│   ├── settings.py          # Project settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── chatbot/                 # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URL routing
│   ├── admin.py             # Admin configuration
│   ├── eligibility.py       # Eligibility checking logic
│   ├── smart_search.py      # Search functionality
│   ├── utils.py             # Utility functions
│   ├── ML/                  # Machine Learning models
│   │   ├── Arts and Science.csv
│   │   ├── engineering.csv
│   │   ├── medical.csv
│   │   └── train_model.py   # ML model training script
│   ├── static/              # Static files (CSS, JS)
│   │   └── chatbot/
│   │       └── style.css
│   ├── templates/           # HTML templates
│   │   └── chatbot/
│   │       ├── home.html
│   │       ├── chat.html
│   │       ├── login.html
│   │       ├── signup.html
│   │       └── history.html
│   └── migrations/          # Database migrations
```

## 🔧 Usage

### Access the Chatbot
1. Open your browser and go to `http://localhost:8000`
2. Sign up for a new account or login
3. Start asking college-related questions
4. View your chat history anytime

### Admin Panel
Access the admin panel at `http://localhost:8000/admin` with your superuser credentials to:
- Manage user accounts
- View search history
- Monitor student profiles
- Manage database records

## 🤖 Machine Learning Models

The chatbot uses trained ML models for three domains:
- **Arts and Science**: Handles queries related to arts and science programs
- **Engineering**: Addresses engineering program inquiries
- **Medical**: Responds to medical program questions

### Training Models
To retrain the ML models with new data:
```bash
python chatbot/ML/train_model.py
```

## 📊 Key Models

### StudentProfile
- Stores student information
- Tracks course preferences
- Maintains user preferences

### SearchHistory
- Records all search queries
- Links to user and conversation
- Enables personalized recommendations

## 🔐 Security Features

- User authentication system
- Password encryption
- Session management
- CSRF protection (Django built-in)

## 🐛 Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Issues
```bash
# Reset database
python manage.py migrate --run-syncdb
```

### Virtual Environment Issues
Deactivate and reactivate:
```bash
deactivate
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
```

## 📦 Dependencies

Main packages used (see `requirements.txt` for complete list):
- Django
- Python-decouple
- Pillow
- scikit-learn
- pandas
- numpy

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💼 Author

**Pragadeesh**
- GitHub: [@pragadeesh1209](https://github.com/pragadeesh1209)
- Repository: [GuidX](https://github.com/pragadeesh1209/GuidX)

## 📞 Support

For issues, questions, or suggestions, please:
- Open an issue on GitHub
- Contact the project maintainer

## 🎓 Acknowledgments

- Django community for the excellent framework
- scikit-learn for ML capabilities
- All contributors and testers

---

**Last Updated**: June 2026
