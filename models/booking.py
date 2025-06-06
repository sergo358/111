from pydantic import BaseModel

class Booking(BaseModel):
    id: int
    user_id: int
    specialist_id: int
    service_id: int
    date: str
    time: str
    status: str = "booked"