# KN 27.03.2023 - packet Simulation - 17.03.2023 Abgabe
# Marcel Biselli, Timo Haas, Emanuel Kupke, Oskar Borkenhagen und Bence Stuhlmann
from queue import PriorityQueue as PrioQ


class Simulation:
    simulation_time = 0
    event_queue = PrioQ()

    def __init__(self, sim_end: int = 10):
        self.sim_end = sim_end
        self.quelle = Quelle(self)
        self.link = Link(self)
        self.sink = Sink(self)

    def start_sim(self):
        self.event_queue.put((3, Event(0, Quelle.newPacketEvent, self, 3, Packet())))
        while Simulation.simulation_time < self.sim_end:
            tmp = []
            for x, y in self.event_queue.queue:
                if y.zeitpunkt == Simulation.simulation_time:
                    tmp.append(y)
                    self.event_queue.queue.remove((x, y))
            for event in tmp:
                event.execute()
        print(f"\nArrived Packets: {self.sink.arrived}")
        print(f"Dropped Packets: {self.link.buffer.dropped}")

    def stop_event(self):
        pass


class Event:
    def __init__(self, zeitpunkt, typ, sim, prio: int, packet):
        self.typ = typ
        self.zeitpunkt = zeitpunkt
        self.simulation = sim
        self.priority = prio
        self.packet = packet

    def execute(self):
        print(f"Executing {self}")
        match self.typ:
            case Quelle.newPacketEvent:
                self.simulation.link.schedule_packet(self.zeitpunkt, self.packet)
                self.simulation.quelle.new_packet_event(self.zeitpunkt)
                Simulation.simulation_time += 1
                print(
                    f"============================== simulation_time {Simulation.simulation_time} ==============================================="
                    + ("" if (Simulation.simulation_time >= 10) else "="))
            case Link.packetDepartureEvent:
                self.simulation.sink.packet_arrival_event(self.zeitpunkt, self.simulation.link.sending_packet)
                self.simulation.link.sending_packet = self.simulation.link.buffer.pop()
                if not self.simulation.link.sending_packet:
                    self.simulation.link.sending = False
                else:
                    self.simulation.link.packet_departure_event(self.zeitpunkt)
            case Sink.packetArrivalEvent:
                self.simulation.sink.arrived += 1
                print(f"Packet {self.packet} arrived at {self.zeitpunkt}")
            case _:
                print("quack")

        print(f"{self.simulation.link.buffer}")

    def __str__(self):
        return f"Event(time: {self.zeitpunkt}, type: {self.typ}, prio: {self.priority}, {self.packet},  "

    def __gt__(self, other):
        return self.priority > other.priority


class Packet:
    packetCount = 1

    def __init__(self):
        self.id = self.packetCount
        Packet.packetCount += 1

    def __repr__(self):
        self.__str__()

    def __str__(self):
        return f"P:{self.id}"


class Quelle:
    newPacketEvent = "newPacketEvent"

    def __init__(self, sim):
        self.simulation = sim

    def new_packet_event(self, cur_time):
        e = Event(cur_time + self.iat_fun(), Quelle.newPacketEvent, self.simulation, 3, Packet())
        self.simulation.event_queue.put((e.priority, e))

    def packet_size_fun(self):
        pass

    @staticmethod
    def iat_fun():
        return 1


class Link:
    packetDepartureEvent = "packetDepartureEvent"

    def __init__(self, sim):
        self.simulation = sim
        self.buffer = Buffer()
        self.sending = False
        self.sending_packet = None

    def schedule_packet(self, zeitpunkt, packet):
        if self.sending:
            self.buffer.add(packet)
        else:
            self.sending_packet = packet
            self.sending = True
            self.packet_departure_event(zeitpunkt)

    def packet_departure_event(self, zeitpunkt):
        e = Event(zeitpunkt + self.prop_time(), Link.packetDepartureEvent, self.simulation, 1, self.sending_packet)
        self.simulation.event_queue.put((e.priority, e))

    @staticmethod
    def prop_time():
        return 2


class Sink:
    packetArrivalEvent = "packetArrivalEvent"

    def __init__(self, sim):
        self.simulation = sim
        self.arrived = 0

    def packet_arrival_event(self, zeitpunkt, packet):
        e = Event(zeitpunkt + self.dis_time(), Sink.packetArrivalEvent, self.simulation, 2,
                  packet)
        self.simulation.event_queue.put((e.priority, e))

    @staticmethod
    def dis_time():
        return 5


class Buffer:

    def __init__(self, size=2):
        self.buffer = []
        self.size = size
        self.dropped = 0

    def add(self, packet: Packet):
        if len(self.buffer) >= self.size:
            print(f"Buffer overflow! Packet {packet.id} dropped at {Simulation.simulation_time}!")
            self.dropped += 1
            return False
        else:
            self.buffer.append(packet)
            return True

    def pop(self):
        if len(self.buffer) <= 0:
            return None
        return self.buffer.pop(0)

    def __str__(self):
        return f"Buffer: {[str(x) for x in self.buffer]}"


Simulation(10).start_sim()
