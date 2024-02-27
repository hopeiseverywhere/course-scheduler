# Stores data about classroom
class Room:
    # ID counter used to assign IDs automatically
    _next_room_id = 0

    # Initializes room data and assign ID to room
    def __init__(self, name: str, number_of_seats: int):
        # room ID - automatically assigned
        self.id = Room._next_room_id
        Room._next_room_id += 1
        # room name in string
        self.name = name
        # number of seats in room in int
        self.number_of_seats = number_of_seats

    def __hash__(self):
        return hash(self.id)

    # Compares ID's of two objects which represent rooms
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    def __str__(self):
        return (f"Room ID: {self.id}, Name: {self.name}, "
                f"Number of Seats: {self.number_of_seats}")

    # Restarts ID assignments
    @staticmethod
    def restart_id() -> None:
        Room._next_room_id = 0
