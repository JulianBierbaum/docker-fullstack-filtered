class MissingTicketException(Exception):
    def __init__(self):
        super().__init__("Ticket not found in the db.")
