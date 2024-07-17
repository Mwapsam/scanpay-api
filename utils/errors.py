from django.db import IntegrityError


class InsufficientBalanceError(IntegrityError):
    def __init__(self, message="Insufficient balance to perform the operation."):
        self.message = message
        super().__init__(self.message)


class AccessTokenError(Exception):
    pass


class TransferRequestError(Exception):
    def __init__(
        self, message="Transfer request failed", status_code=None, response_text=None
    ):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class TransferRequestError(Exception):
    pass


class TransactionError(Exception):
    def __init__(
        self, message="Transaction failed", status_code=None, response_text=None
    ):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)
