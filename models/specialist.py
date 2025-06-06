from pydantic import BaseModel

class Specialist(BaseModel):
    id: int
    name: str
    avatar: str
    bio: str