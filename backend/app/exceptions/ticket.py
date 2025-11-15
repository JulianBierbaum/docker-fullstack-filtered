class MissingTicketException(Exception):
    def __init__(self):
        super().__init__(f"Ticket not found in the db.")
