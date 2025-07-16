from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class ArtistCreate(BaseModel):
    name: str

class SongCreate(BaseModel):
    title: str
    artist_id: int

class PlaylistCreate(BaseModel):
    name: str

class Artist(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class Song(BaseModel):
    id: int
    title: str
    artist_id: int

    class Config:
        from_attributes = True

class Playlist(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
