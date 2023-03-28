import time as t


class Simulation:

    def __init__(self):
        self.events = [Source(0, 1, None)]
        self.simulation_time = 0
        self.system_state = SystemState([], 0, None, 0, 0)
        self.running = True

    def stop(self):
        self.running = False
        return self

    def add_event(self, event):
        self.events.append(event)

    def run(self):
        while self.running:
            print(self)

            self.add_event(Source(0, 1, None))
            if len(self.events) > 2:
                self.stop()
            self.simulation_time += 1
            t.sleep(1)

    def __str__(self):
        return f"Simulation time: {self.simulation_time}\n" \
               f"Events: {self.events}\n" \
               f"System state: {self.system_state}\n"


class SystemState:
    def __init__(self, queue, queue_max_size, current, dropped, arrived):
        self.queue = queue
        self.queue_max_size = queue_max_size
        self.current = current
        self.dropped = dropped
        self.arrived = arrived

    def move_to_current(self):
        self.current = self.queue.pop(0)
        return self.current

    def add(self, packet):
        self.queue.append(packet)

    def __str__(self):
        return f"Queue max size: {self.queue_max_size}\n" \
               f"Queue: {self.queue}\n" \
               f"Current: {self.current}\n" \
               f"Dropped: {self.dropped}\n" \
               f"Arrived: {self.arrived}\n"


class Packet:
    def __init__(self, name, size):
        self.name = name
        self.size = size


class Event:
    def __init__(self, time, priority, args):
        self.time = time
        self.priority = priority
        self.args = args


class Source(Event):
    def __init__(self, time, priority, args):
        super().__init__(time, priority, args)

    @staticmethod
    def new_packet(name, size):
        return Packet(name, size)

    def __repr__(self):
        return f"Source: {self.time} {self.priority} {self.args}"


class Link(Event):
    def __init__(self, time, priority, args):
        super().__init__(time, priority, args)

    @staticmethod
    def packet_departure(packet):
        return packet

    def __repr__(self):
        return f"Link: {self.time} {self.priority} {self.args}"
