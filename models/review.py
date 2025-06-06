from pydantic import BaseModel

class Review(BaseModel):
    id: int
    user_id: int
    specialist_id: int
    text: str
    stars: int
    created: str