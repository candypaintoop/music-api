from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class SongBase(BaseModel):
    title: str
    artist_id: int

class SongCreate(SongBase):
    pass

class Song(SongBase):
    id: int

    class Config:
        from_attributes = True

class ArtistBase(BaseModel):
    name: str

class ArtistCreate(ArtistBase):
    pass

class Artist(ArtistBase):
    id: int

    class Config:
        orm_mode = True

class PlaylistBase(BaseModel):
    name: str

class PlaylistCreate(PlaylistBase):
    pass

class Playlist(PlaylistBase):
    id: int

    class Config:
        orm_mode = True
