import inflect


class BusinessLogicException(Exception):
    """Base class for business logic exceptions."""
    def __init__(self, message: str, code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code


class PlayerNotFoundException(BusinessLogicException):
    def __init__(self, name):
        super().__init__(f"Player '{name}' has not bought in yet.", code=400)


class InvalidInputException(BusinessLogicException):
    def __init__(self, input_name, input_value, allowed_values):
        p = inflect.engine()
        input_name_pl = p.plural(input_name, len(allowed_values))

        msg = f"Invalid {input_name}: '{input_value}'. Allowed {input_name_pl}: {', '.join(allowed_values)}."
        super().__init__(msg, code=422)