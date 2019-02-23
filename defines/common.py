import enum
from threading import Lock


class EncodeTask(object):

    def __init__(self, filename, output_name, bit_rate_vid, fps, res):
        self.filename = filename
        self.output_name = output_name
        self.bit_rate_vid = bit_rate_vid
        self.fps = fps
        self.res = res


class PacketType(enum.Enum):

    ENCODE_TASK = 0
    COMMAND = 1
    STATUS = 2


class Status(enum.Enum):

    TASK_DONE = 0
    WORKING = 1


class Command(enum.Enum):

    GET_PROGRESS = 0
    SHUTDOWN = 1


class Packet(object):

    def __init__(self, packet_type):
        self.type = packet_type


class SynchronizedTaskCounter(object):

    def __init__(self):
        self._fin_lock = Lock()
        self._prog_lock = Lock()
        self._finished_task_count = 0
        self._in_progress_count = 0

    def inc_prog_count(self):
        self._prog_lock.acquire()
        self._in_progress_count += 1
        self._prog_lock.release()

    def dec_prog_count(self):
        self._prog_lock.acquire()
        self._in_progress_count -= 1
        self._prog_lock.release()

    def inc_fin_count(self):
        self._fin_lock.acquire()
        self._finished_task_count += 1
        self._fin_lock.release()

    def get_fin_count(self):
        self._fin_lock.acquire()
        fin_count = self._finished_task_count
        self._fin_lock.release()
        return fin_count

    def get_prog_count(self):
        self._prog_lock.acquire()
        prog_count = self._in_progress_count
        self._prog_lock.release()
        return prog_count

