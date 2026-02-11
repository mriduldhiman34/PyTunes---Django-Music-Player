# 🎧 **PyTunes — Django Music Player**

**PyTunes** is a web-based **music streaming & playback application** built with **Django** that integrates with **YouTube Music** using APIs and download tools. It allows users to search real songs, stream audio, view lyrics, and manage a music queue — all inside a clean browser interface.

This project was built as part of your **BCA semester project** and demonstrates real-world API integration with Django.

---

## 🚀 **Key Features**

PyTunes supports:

* 🔍 **Search any song from YouTube Music**
* 🎵 **Stream audio directly in the browser**
* 📜 **Fetch and display song lyrics**
* 📋 **Add songs to a queue**
* ▶️ **Play next/previous from queue**
* 🎨 **Custom UI with HTML, CSS & JavaScript**
* ⚡ **Fast performance using yt-dlp backend**
* 🌐 **Live YouTube Music data via ytmusicapi**

---

## 🛠️ **Tech Stack**

| Component       | Technology Used           |
| --------------- | ------------------------- |
| Backend         | Django (Python)           |
| Music Fetching  | ytmusicapi                |
| Audio Streaming | yt-dlp                    |
| Frontend        | HTML, CSS, JavaScript     |
| Templates       | Django Template Engine    |
| Server          | Django Development Server |

---

## 📂 **Project Structure (Simplified)**

```
PyTunes/
│── Music_Player/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
│── main/
│   ├── views.py
│   ├── models.py
│   └── urls.py
│
│── static/
│   ├── style.css
│   ├── script.js
│
│── templates/
│   └── index.html
│
│── manage.py
│── requirements.txt
│── .gitignore
```

---

## ▶️ **How It Works (Behind the Scenes)**

1. User searches a song
2. PyTunes uses **ytmusicapi** to find matching results
3. Selected song is processed using **yt-dlp**
4. Audio stream is sent to the browser player
5. Lyrics are fetched and displayed
6. Song is added to playback queue

This makes PyTunes behave like a lightweight YouTube Music clone.

---

## ▶️ **Run This Project Locally**

### Step 1 — Clone the repo

```bash
git clone https://github.com/mriduldhiman34/PyTunes---Django-Music-Player.git
cd PyTunes---Django-Music-Player
```

### Step 2 — Create virtual environment

```bash
python -m venv .env
```

### Step 3 — Activate venv

**Windows (PowerShell):**

```bash
.env\Scripts\activate
```

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Run server

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/index/
```

---

## 🔐 Security Note

All API keys, OAuth tokens, and sensitive browser data are **excluded from GitHub** using `.gitignore`. The app works with locally stored credentials only.

---

## 🎯 Learning Outcomes

Through this project, you demonstrated:

* Django full-stack development
* Working with real-world APIs
* Handling media streaming
* Managing queues in JavaScript
* Using Git & GitHub professionally

---

## 🤝 Contributing

Feel free to fork this repository, add features, improve UI, or submit pull requests.

---

## 👤 Author

**Mridul Dhiman**

GitHub: **@mriduldhiman34**

⭐ If you like this project, give it a star on GitHub!
