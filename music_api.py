from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
from pydantic import BaseModel
import models, schemas
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Music API with JWT Auth")
app.mount("/", StaticFiles(directory=".", html=True), name="static")
api = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()

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

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
    

@api.post("/api/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

class LoginData(BaseModel):
    username: str
    password: str

@api.post("/api/login")
def login(data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == data.username).first()
    if not db_user or not verify_password(data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@api.get("/api/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {"username": current_user.username, "id": current_user.id}

@api.get("/api/artists")
def get_artists(db: Session = Depends(get_db)):
    return db.query(models.Artist).all()

@api.post("/api/artists")
def create_artist(artist: schemas.ArtistCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_artist = models.Artist(name=artist.name)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

@api.get("/api/songs")
def get_songs(db: Session = Depends(get_db)):
    return db.query(models.Song).all()

@api.post("/api/songs")
def add_song(song: schemas.SongCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    artist = db.query(models.Artist).filter(models.Artist.id == song.artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    new_song = models.Song(title=song.title, artist_id=song.artist_id)
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song

@api.get("/api/playlists")
def get_playlists(db: Session = Depends(get_db)):
    return db.query(models.Playlist).all()

@api.post("/api/playlists")
def create_playlist(playlist: schemas.PlaylistCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_playlist = models.Playlist(name=playlist.name, owner_id=current_user.id)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


app.include_router(api, prefix="/api")


