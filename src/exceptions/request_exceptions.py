import typing


class BadRequestError(Exception):
    error_dict: typing.ClassVar = None

    def __init__(self, *args, error_dict: dict | None = None) -> None:
        super().__init__(*args)
        self.error_dict = error_dict


class InvalidJSONError(BadRequestError):
    error_dict: typing.ClassVar = {"data": "invalid_json"}

    def __init__(self, *args, error_dict: dict | None = None) -> None:
        super().__init__(*args)
        self.error_dict = error_dict
