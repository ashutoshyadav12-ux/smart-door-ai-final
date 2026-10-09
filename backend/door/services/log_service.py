from ..models import AccessLog


def log_event(event_type, person=None, confidence=None, device="", detail=""):
    return AccessLog.objects.create(person=person, event_type=event_type,
                                    confidence=confidence, device=device, detail=detail)


def query_logs(params):
    qs = AccessLog.objects.select_related("person")
    if params.get("event_type"):
        qs = qs.filter(event_type=params["event_type"].upper())
    if params.get("person"):
        qs = qs.filter(person_id=params["person"])
    if params.get("q"):
        qs = qs.filter(person__full_name__icontains=params["q"])
    if params.get("date_from"):
        qs = qs.filter(timestamp__date__gte=params["date_from"])
    if params.get("date_to"):
        qs = qs.filter(timestamp__date__lte=params["date_to"])
    return qs
