from fastapi import Request


def flash(request: Request, message: str, level: str = "success") -> None:
    flashes = request.session.get("_flashes", [])
    flashes.append({"message": message, "level": level})
    request.session["_flashes"] = flashes


def consume_flashes(request: Request) -> list[dict]:
    return request.session.pop("_flashes", [])
