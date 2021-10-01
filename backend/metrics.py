from models import Verification


def get_user_rating(user_id):
    sources = len(Verification.query.filter(
        Verification.destination_user_id.like(user_id) & Verification.verdict_of_human.is_(True)).all())
    destinations = len(Verification.query.filter(
        Verification.source_user_id.like(user_id) & Verification.verdict_of_human.is_(True)).all())

    if sources + destinations == 0:
        return 0

    sources = sources * sources
    return round((destinations - sources) / (destinations + sources), 2)
