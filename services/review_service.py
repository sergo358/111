from db.repositories import add_review, get_reviews_for_specialist

class ReviewService:
    @staticmethod
    async def add(user_id, specialist_id, text, stars):
        return await add_review(user_id, specialist_id, text, stars)

    @staticmethod
    async def list_for_specialist(spec_id):
        return await get_reviews_for_specialist(spec_id)