# 🎵 Music API — FastAPI + JWT Auth + SQLite

## 🌟 Overview
A secure RESTful Music API:
- Built with **FastAPI**, **SQLAlchemy**, **SQLite**
- JWT Authentication for user signup, login, and protected routes
- CRUD for **Artists**, **Songs**, and **Playlists**
- Fully tested with **Pytest**
- Live deployed on **Render**
- Interactive API Docs with **Swagger UI**

## 📌 Live Demo
- 🌐 [Deployed API on Render](https://music-api-oqci.onrender.com)
- 📜 [Swagger UI Docs](https://music-api-oqci.onrender.com/docs)

## 📌 Features
- ✅ **Register / Login** with JWT Auth
- ✅ **/me** protected route
- ✅ CRUD: **Artists**, **Songs**, **Playlists**
- ✅ SQLite database (easy to switch to PostgreSQL)
- ✅ Pytest tests included
- ✅ Easy deployment on Render

## 🛠️ Tech Stack
- FastAPI
- SQLAlchemy
- SQLite
- python-jose (JWT)
- passlib (password hashing)
- Pytest
- Uvicorn

## 🧪 Tests
Run locally:
```bash
pytest test_main.py
