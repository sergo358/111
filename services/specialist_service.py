from db.repositories import get_all_specialists, get_specialist, get_services_for_specialist

class SpecialistService:
    @staticmethod
    async def list_specialists():
        return await get_all_specialists()

    @staticmethod
    async def get_specialist(spec_id):
        return await get_specialist(spec_id)

    @staticmethod
    async def list_services(spec_id):
        return await get_services_for_specialist(spec_id)