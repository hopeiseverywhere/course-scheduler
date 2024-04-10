from model import Constant
from typing import Dict

class Reservation:
    """
    Represents a reservation for a particular day, time, and room.

    Attributes:
        NR (int): Number of rooms available.
        _reservation_pool (Dict[int, 'Reservation']): A dictionary to store reservation objects hashed by their unique hash codes.
        day (int): The day of the reservation.
        time (int): The time slot of the reservation, note the time is relative.
        room_id (int): The ID of the room reserved.
    """
    NR = -1 # number of rooms
    _reservation_pool: Dict[int, 'Reservation'] = {}

    def __init__(self, day: int, time: int, room: int):
        self.day = day
        self.time = time
        self.room_id = room

    @staticmethod
    def parse(hash_code):
        """Parses a hash code into a Reservation object.

        Args:
            hash_code (int): The hash code representing the reservation

        Returns:
            Reservation: A Reservation object corresponding to the hash code.
        """
        reservation = Reservation._reservation_pool.get(hash_code)
        if reservation is None:
            day = hash_code // (Constant.DAY_SLOTS * Reservation.NR)
            hash_code2 = hash_code - (day * Constant.DAY_SLOTS * Reservation.NR)
            room = hash_code2 // Constant.DAY_SLOTS
            time = hash_code2 % Constant.DAY_SLOTS
            reservation = Reservation(day, time, room)
            Reservation._reservation_pool[hash_code] = reservation
        return reservation

    @staticmethod
    def get_hash_code(day: int, time: int, room: int):
        """
        Generates a hash code for a given combination of day, time, and room.

        Args:
            day (int): The day of the reservation.
            time (int): The time slot of the reservation, note the time relative time.
            room (int): The ID of the room reserved.

        Returns:
            int: The hash code representing the reservation.
        """
        return (day * Reservation.NR * Constant.DAY_SLOTS
                + room * Constant.DAY_SLOTS + time)

    @staticmethod
    def get_reservation(nr: int, day: int, time: int, room: int):
        """
        Retrieves a reservation object or creates a new one if not found.

        Args:
            nr (int): Number of rooms.
            day (int): The day of the reservation.
            time (int): The time slot of the reservation, note the time is relative.
            room (int): The ID of the room reserved.

        Returns:
            Reservation: A Reservation object.
        """
        if nr != Reservation.NR and nr > 0:
            Reservation.NR = nr
            Reservation._reservation_pool.clear()
        hash_code = Reservation.get_hash_code(day, time, room)
        reservation = Reservation.parse(hash_code)

        if reservation is None:
            reservation = Reservation(day, time, room)
            Reservation._reservation_pool[hash_code] = reservation
        return reservation

    def __hash__(self) -> int:
        return Reservation.get_hash_code(self.day, self.time, self.room_id)
