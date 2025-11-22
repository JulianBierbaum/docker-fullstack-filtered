class DatabaseException(Exception):
    def __init__(self, error: str):
        super().__init__(f"Database error occurred: {error}")
