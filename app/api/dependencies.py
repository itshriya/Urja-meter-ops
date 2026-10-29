from fastapi import Request


def get_portal_client(request: Request):
    return request.app.state.portal_client