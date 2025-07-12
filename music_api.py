from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from fastapi.responses import JSONResponse

import models, schemas
from database import SessionLocal, engine, Base

# Create DB tables
Base.metadata.create_all(bind=engine)

# ✅ Init app & limiter
app = FastAPI(title="Music API with JWT Auth + Rate Limiting")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Slow down!"},
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ✅ SIGNUP with rate limit
@app.post("/signup")
@limiter.limit("5/minute")
def signup(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# ✅ LOGIN with rate limit
@app.post("/login")
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# ✅ ARTIST CRUD
@app.post("/artists")
def create_artist(artist: schemas.ArtistCreate, db: Session = Depends(get_db)):
    db_artist = models.Artist(name=artist.name)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

@app.get("/artists")
def get_artists(db: Session = Depends(get_db)):
    return db.query(models.Artist).all()

# ✅ SONG CRUD
@app.post("/songs")
def add_song(song: schemas.SongCreate, db: Session = Depends(get_db)):
    artist = db.query(models.Artist).filter(models.Artist.id == song.artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    new_song = models.Song(title=song.title, artist_id=song.artist_id)
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song

@app.get("/songs")
def get_songs(db: Session = Depends(get_db)):
    return db.query(models.Song).all()

# ✅ PLAYLIST CRUD
@app.post("/playlists")
def create_playlist(playlist: schemas.PlaylistCreate, db: Session = Depends(get_db)):
    db_playlist = models.Playlist(name=playlist.name)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@app.get("/playlists")
def read_playlists(db: Session = Depends(get_db)):
    return db.query(models.Playlist).all()
