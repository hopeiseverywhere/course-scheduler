from model import Constant


class Reservation:
    NR = -1
    _reservation_pool = {}

    def __init__(self, day: int, time: int, room: int):
        self.day = day
        self.time = time
        self.room_id = room

    @staticmethod
    def parse(hash_code):
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
        return (day * Reservation.NR * Constant.DAY_SLOTS
                + room * Constant.DAY_SLOTS + time)

    @staticmethod
    def get_reservation(nr: int, day: int, time: int, room: int):
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
