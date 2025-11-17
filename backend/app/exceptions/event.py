class MissingEventException(Exception):
    def __init__(self):
        super().__init__("Location not found in the db.")


class WrongRoleException(Exception):
    def __init__(self, user: str):
        super().__init__(f"User '{user}' is not an ORGANIZER.")
