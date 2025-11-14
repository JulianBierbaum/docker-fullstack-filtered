class DuplicateLocationNameException(Exception):
    def __init__(self, name: str):
        super().__init__(f"Location with name '{name}' already exists in the db.")


class MissingLocationException(Exception):
    def __init__(self):
        super().__init__(f"Location not found in the db.")
