class BaseAPIException(Exception):
    status_code = 500


class InvalidRequestException(BaseAPIException):
    status_code = 400


class NotFoundException(BaseAPIException):
    status_code = 404


class ConflictException(BaseAPIException):
    status_code = 409


class MissingRequiredFieldException(InvalidRequestException):
    pass


class UserAlreadyExistsException(ConflictException):
    pass


class GroupAlreadyExistsException(ConflictException):
    pass


class UserNotFoundException(NotFoundException):
    pass


class GroupNotFoundException(NotFoundException):
    pass
