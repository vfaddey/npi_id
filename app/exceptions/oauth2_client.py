from app.exceptions.base import NPIException


class ClientNotFound(NPIException):
    ...

class ClientAlreadyExists(NPIException):
    ...