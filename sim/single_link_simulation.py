# import class from library ans give it a name
from queue import PriorityQueue as PrioQ
# import (higher order) function
from functools import total_ordering
# import function expovariate under the name exprnd
# expovariate generates random number according to an exponential distribution
from random import expovariate as exprnd


# Sim: global simulation class
class Sim:
    # class variables
    t = 0  # simulation time
    evQ = PrioQ()  # initialize emt
    stop = False

    # constructor
    def __init__(self):
        Sim.evQ = PrioQ()
        Sim.t = 0
        Sim.stop = False

    # run method
    @staticmethod
    def run():
        while not Sim.evQ.empty():
            sim_ev = Sim.evQ.get()
            Sim.t = sim_ev.t
            sim_ev.work()
            if Sim.stop:
                break

    # stop method
    @staticmethod
    def stop():
        pass  # needs to be implemented


@total_ordering  # provides all ordering functions if __lt__ and __eq__ are given
class Event:
    # class attributes
    n = 0  # event counter

    # constructor
    def __init__(self, t, prio, fun, args=[]):  # assigns an empty list as default value to argument args
        # instance attributes
        self.t = t  # event time
        self.prio = prio  # event priority
        self.n = Event.n  # event number (generated from class attribute)
        Event.n += 1  # increase class attribute n
        self.fun = fun  # working function
        self.args = args  # arguments of working function

    # make event comparable and sortable by defining __lt__(less than) and __eq__(equal)
    def __lt__(self, other):
        return (self.t, self.prio, self.n) < (other.t, other.prio, other.n)

    def __eq__(self, other):
        return (self.t, self.prio) == (other.t, other.prio)


# define event classes (reason for event classes is to
# - define priorities for ordering
# - define names for printing debug/simulation information


class NewPacketEvent(Event):
    prio = 3
    name = 'NewPacketEvent'

    def __init__(self, t, fun, args):
        # call constructor from upper class
        # general: use super() to call method from upper class
        super().__init__(t, NewPacketEvent.prio, fun, args)


class PacketArrivalEvent(Event):
    prio = 2
    name = 'PacketArrivalEvent'

    def __init__(self, t, fun, args):
        super().__init__(t, PacketArrivalEvent.prio, fun, args)


class PacketDepartureEvent(Event):
    prio = 1
    name = 'PacketDepartureEvent'

    def __init__(self, t, fun, args):
        super().__init__(t, PacketDepartureEvent.prio, fun, args)


class StopEvent(Event):
    pass  # needs to be implemented


class Packet:
    # a packet with size and name
    def __init__(self, name, size):
        # instance attributes
        self.name = name
        self.size = size


class Source:
    # a source generates packets according to iat_fun() and packet_size_fun()
    # and gives packets to recipient
    # iat_fun() yields an inter_arrival_time, packet_size_fun() a packet_size
    def __init__(self, name, iat_fun, packet_size_fun, recipient):
        self.name = name
        # number packets to give them a unique name
        self.packet_num = 1
        self.iat_fun = iat_fun
        self.packet_size_fun = packet_size_fun
        self.recipient = recipient

    def new_packet(self):
        # generate packet with name "Q-n" if Q is the name of the source and "n" is the packet number
        # note that f'' is a formatted string; with {code} you can insert code that's interpreted when printing
        packet = Packet(f'{self.name}-{self.packet_num}', self.packet_size_fun())
        self.packet_num += 1
        # give packet to recipient (in the single queue example the Link)
        self.recipient.packet_arrival(packet)
        # genentae next arrival event and put it
        ev = NewPacketEvent(Sim.t + self.iat_fun(), self.new_packet, [])  # note that Sim.t is a class attribute
        Sim.evQ.put(ev)


class Buffer:
    # a buffer is used to store packets up to a certain volume
    # use method push() to put packets in the buffer; push() yields False if the packet is dropper
    # use method pop() to get the next packet from the buffer; pop() yields None if the buffer is empty
    # method empty() checks if the buffer is empty
    def __init__(self, volume):
        self.volume = volume  # volume [Bits] of the buffer
        self.occupied = 0  # occupied volume
        self.packetL = list()  # list of buffer packets; list() generates empty list

    def push(self, packet):
        # check if there enough room
        if self.volume - self.occupied >= packet.size:
            self.packetL.append()  # method append() adds element to list
            self.occupied += packet.size
            return True
        else:
            return False

    def pop(self):
        if self.packetL:  # an empty list yields False, otherwise True
            packet = self.packetL.pop(0)  # method pop(i) extracts element at index i from list
            self.occupied -= packet.size
            return packet
        else:
            return None


class Link:
    # a Link receives packets and transmits them to the recipient
    # it buffer packets if it cannot transmit them immediately

    # constructor
    def __init__(self, name, rate, delay, buffer_volume, recipient):
        self.name = name  # name of the link to display simulation/debugging information
        self.rate = rate  # rate or capacity of the link [bps]
        self.delay = delay  # propagation delay of the link [s]
        self.buffer = Buffer(buffer_volume)  # Buffer for waiting packets with size buffer_volume
        self.recipient = recipient  # node that gets the transmitted packets
        self.packet_in_transmission = None  # packet that is currently transmitted

    # new packet arrives at the link
    def packet_arrival(self, packet):
        # try to put it in the buffer
        if self.buffer.push():
            # initiate a transmission (if possible)
            self.start_transmitting()
        else:
            # print information that packet is dropped
            print(f'{Sim.t}: Packet {packet.name} dropped')
            # you may also take statistics here

    # starts a transmission if (1) there is no ongoing transmission and (2) a packet is in the buffer
    def start_transmitting(self):
        if self.packet_in_transmission:  # on_going transmission? Note: None evaluates to False in a Boolean expression
            return
        packet = self.buffer.pop()  # try to get packet from buffer
        if packet:  # if there was a packet in the buffer
            # note the packet in transmission
            self.packet_in_transmission = packet
            # generate packet departure event and put in in the event list
            ev = PacketDepartureEvent(Sim.t + packet.size / self.rate, self.packet_departure, [])
            Sim.evQ.put(ev)

    # transmission of packet is finished
    # packet travels through the cable and arrives after the propagation delay at the recipient (the sink)
    def packet_departure(self):
        # generate PacketArrivalEvent and put it in event list
        ev = PacketArrivalEvent(Sim.t + self.delay, self.recipient.packet_arrival, self.packet_in_transmission)
        Sim.evQ.put(ev)
        # reset packet_in_transmision and try to send next packet
        self.packet_in_transmission = None
        self.start_transmitting()


# generates packet size
def packet_size_fun():
    mean_packet_size = 2000  # 2000 Bits
    return mean_packet_size
    # return exprnd(1/mean_packet_size) # produces random values with mean 1000 according to an exponential distribution


def iat_fun():
    mean_iat = 0.001
    return mean_iat
    # return exprnd(1/mean_iat) # # produces random values with mean 0.0 according to an exponential distribution


class Sink:
    pass  # needs to be implemented


sink = Sink()

# simulation paramters
rate = 1e6  # 1 Mbps
propagation_delay = 0.01  # 10 ms
buffer_volume = 4000  # bits
sim_end_tine = 100  # seconds
# instantiate the link L1 with rate 1 Mbps
link = Link('L1', rate, propagation_delay, buffer_volume, sink)

source = Source('Q1', iat_fun, packet_size_fun, link)

sim = Sim()
first_arrival_event = NewPacketEvent(0, source.new_packet, [])
Sim.evQ.put(first_arrival_event)
stop_event = StopEvent(sim_end_tine, Sim.stop, [])
Sim.evQ.put(stop_event)
Sim.run()
