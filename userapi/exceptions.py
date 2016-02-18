class BaseAPIException(Exception):
    status_code = 500


class MissingRequiredFieldException(BaseAPIException):
    status_code = 400


class UserAlreadyExistsException(BaseAPIException):
    status_code = 409


class UserNotFoundException(BaseAPIException):
    status_code = 404
