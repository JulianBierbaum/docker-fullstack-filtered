class DuplicateEmailException(Exception):
    def __init__(self, email: str):
        super().__init__(f"Email '{email}' already exists in the db.")


class MissingUserException(Exception):
    def __init__(self, user: str | None = None):
        if not user:
            msg = "User not found in the db."
        else:
            msg = f"User with name '{user}' not found in the db."
        super().__init__(msg)
