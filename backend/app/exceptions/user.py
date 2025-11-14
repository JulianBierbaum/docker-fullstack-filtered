class DuplicateEmailException(Exception):
    def __init__(self, email: str):
        super().__init__(f"Email '{email}' already exists in the db.")


class MissingUserException(Exception):
    def __init__(self, user: str):
        super().__init__(f"User '{user}' not found in the db.")
