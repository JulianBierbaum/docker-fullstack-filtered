class MissingBookingException(Exception):
    def __init__(self):
        super().__init__("Booking not found in the db.")
