from app.exceptions.base import NPIException


class UserAlreadyExistsException(NPIException):
    ...

class UserNotFoundException(NPIException):
    ...

class InvalidCredentialsException(NPIException):
    ...

class AuthenticationException(NPIException):
    ...

class AuthorizationException(NPIException):
    ...