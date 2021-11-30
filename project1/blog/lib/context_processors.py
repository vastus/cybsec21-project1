from django.http import HttpRequest


def current_user(request: HttpRequest):
    # from pprint import pprint
    # print()
    # print()
    # print()
    # print("HERE WE AREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
    # pprint(request.__dict__)
    # print()
    # print()
    # print()

    current_user = None
    if hasattr(request, 'current_user'):
        current_user = request.current_user
    return {"current_user": current_user, 'keke': 'reijo'}
