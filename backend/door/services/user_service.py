from ..ai.cache import cache
from ..models import Person


def delete_person(person: Person):
    person.delete()      # cascades FaceProfiles
    cache.reload()
