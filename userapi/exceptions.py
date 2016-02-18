class BaseAPIException(Exception):
    status_code = 500


class ConflictException(BaseAPIException):
    status_code = 409


class MissingRequiredFieldException(BaseAPIException):
    status_code = 400


class UserAlreadyExistsException(ConflictException):
    pass


class GroupAlreadyExistsException(ConflictException):
    pass


class UserNotFoundException(BaseAPIException):
    status_code = 404
