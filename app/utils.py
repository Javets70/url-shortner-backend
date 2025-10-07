from fastapi import Request


def get_rate_limit_key(request: Request) -> str:
    client_ip = request.client.host
    return f"rate_limit:{client_ip}"
