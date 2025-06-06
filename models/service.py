from pydantic import BaseModel

class Service(BaseModel):
    id: int
    specialist_id: int
    name: str
    duration: int
    price: int
    emoji: str