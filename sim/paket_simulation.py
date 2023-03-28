# KN 27.03.2023 - Paket Simulation - 17.03.2023 Abgabe

class Simulation:
    def __init__(self, simulationszeit):
        pass

    def stop_event(self):
        pass


class Event:
    def __init__(self, zeitpunkt, typ):
        pass


class Paket:
    def __init__(self):
        pass


class Quelle:
    def __init__(self):
        pass

    def newPacketEvent(self):
        pass

    def packet_size_fun(self):
        pass

    def iat_fun(self):
        pass


class Link:
    def __init__(self):
        buffer = None
        rate = None
        delay = None
        prep = None  # Ausbreitungsverzögerung

    def packet_departure_event(self, paket: Paket):
        pass


class Sink:
    def __init__(self):
        pass

    def packet_arrival_event(self, paket: Paket):
        pass

    def debug_stats(self):
        pass


class PriorityQueue:
    def __init__(self):
        pass


class Buffer:
    def __init__(self):
        pass
