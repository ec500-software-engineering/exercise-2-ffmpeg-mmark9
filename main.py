import os
import time
import queue
import random
import argparse
import multiprocessing
from utils import encoder
from threading import Thread
from multiprocessing import Process
from defines.common import Command, Packet, \
    PacketType, SynchronizedTaskCounter, Status, EncodeTask

REPL_MAIN_MENU = '''
*******Welcome to the encoding asynchronous demo!*********

Enter a number and then hit enter to pick an option below:

1. Add a task in the queue
2. View limit on number of concurrent tasks
3. View encoding progress
4. Exit
**********************************************************\n>    
'''


class EncodeWorker(Thread):

    def __init__(self, task_queue, cmd_queue, worker_id, sync_counter):
        super().__init__()
        self._task_queue = task_queue
        self._worker_id = worker_id
        self._cmd_queue = cmd_queue
        self._sync_counter = sync_counter

    def run(self):
        cmd_packet = None
        while True:
            try:
                cmd_packet = self._cmd_queue.get(block=False)
            except queue.Empty:
                pass
            if cmd_packet is not None:
                if cmd_packet.cmd == Command.SHUTDOWN:
                    print(
                        'worker {}: shutting down...'.format(self._worker_id)
                    )
                    break
            try:
                task_packet = self._task_queue.get(block=False)
            except queue.Empty:
                task_packet = None
                pass

            if task_packet is not None:
                encode_task = task_packet.task
                print(
                    'worker {}: starting encode of file {}...'.format(
                        self._worker_id,
                        encode_task.filename
                    )
                )
                self._sync_counter.inc_prog_count()
                ret_code = encoder.Encode.encode_video(
                    encode_task
                )
                # work_queue.task_done()
                if ret_code == 0:
                    print(
                        'worker {}: successfully completed encoding file {}....'.format(
                            self._worker_id,
                            encode_task.filename
                        )
                    )
                else:
                    print(
                        'worker {}: failed to encode file {} | return code {}'.format(
                            self._worker_id,
                            encode_task.filename,
                            ret_code
                        )
                    )
                self._sync_counter.dec_prog_count()
                self._sync_counter.inc_fin_count()
                self._task_queue.task_done()
                task_done_packet = Packet(PacketType.STATUS)
                task_done_packet.status = Status.TASK_DONE
            time.sleep(
                random.randint(1, 3)
            )


def repl_get_input(prompt):
    response = input(prompt)
    return response


def repl_get_new_task():
    choice = 0
    input_filename = repl_get_input(
        'Enter input filename >    '
    )
    output_filename = repl_get_input(
        'Enter output filename >    '
    )
    bit_rate = '1'
    while True:
        try:
            user_input = repl_get_input(
                'Choose video bit rate (hit enter for default 1Mbps):'
                '\n1. 1Mbps 2. 2Mbps \n'
                '>    '
            )
            if user_input == '':
                break
            choice = int(user_input)
            if choice == 1:
                bit_rate = '1'
                break
            elif choice == 2:
                bit_rate = '2'
                break
            else:
                print(
                    '{} is not a valid choice..'.format(
                        choice
                    )
                )
        except ValueError:
            print(
                'Error parsing input: please enter 1 or 2!'
            )

    fps = '30'
    '''while True:
        user_input = repl_get_input(
            'Enter video frame rate (hit enter for default 30fps)\n'
            '>    '
        )
        if user_input == '':
            break
        try:
            choice = int(
                user_input
            )
            if choice >= 1:
                fps = str(choice)
                break
            else:
                print(
                    '{} is not a positive non-zero integer!'.format(choice)
                )
        except ValueError:
            print(
                'Error parsing input: please enter a valid integer for frame rate!'
            )'''

    resolution = '480'
    while True:
        user_input = repl_get_input(
            'Enter video resolution (hit enter for default 480p)\n'
            '1. 480p  2. 720p\n'
            '>    '
        )
        if user_input == '':
            break
        try:
            choice = int(
                user_input
            )
            if choice == 1:
                fps = '480'
                break
            elif choice == 2:
                fps = '720'
                break
            else:
                print(
                    '{} is not a valid choice!'.format(choice)
                )

        except ValueError:
            print(
                'Error parsing input: please enter a valid integer for frame rate!'
            )

    return EncodeTask(
        input_filename,
        output_filename,
        bit_rate,
        fps,
        resolution
    )


def repl_routine(input_queue, output_queue):
    while True:
        choice = repl_get_input(REPL_MAIN_MENU)
        try:
            choice = int(choice)
        except ValueError:
            print(
                'Error parsing input: please enter a valid integer!'
            )
            continue
        if choice == 1:
            encode_task = repl_get_new_task()
            packet = Packet(
                PacketType.ENCODE_TASK
            )
            packet.task = encode_task
            output_queue.put(packet)
        elif choice == 2:
            print(
                'Max number of worker threads configured is {}'.format(
                    multiprocessing.cpu_count()
                )
            )
        elif choice == 3:
            packet = Packet(PacketType.COMMAND)
            packet.cmd = Command.GET_PROGRESS
            output_queue.put(packet)
            response_packet = input_queue.get()
            print(response_packet.data)
        elif choice == 4:
            packet = Packet(PacketType.COMMAND)
            packet.cmd = Command.SHUTDOWN
            output_queue.put(packet)
            break
        else:
            print(
                'Invalid choice, {}, entered; please try again...'
            )


def run_backend(input_queue, output_queue, num_workers):
    thread_list = []
    comm_queues = []
    task_queue = queue.Queue()
    sync_counter = SynchronizedTaskCounter()
    print(
        'backend: starting....'
    )
    for i in range(0, num_workers):
        comm_queues.append(
            queue.Queue()
        )
        thread_list.append(
            EncodeWorker(
                task_queue,
                comm_queues[i],
                i,
                sync_counter
            )
        )
    for i in range(0, num_workers):
        thread_list[i].start()
    packet = None
    while True:
        try:
            packet = input_queue.get(block=False)
        except queue.Empty:
            time.sleep(1)
            continue
        if packet.type == PacketType.COMMAND:
            if packet.cmd == Command.GET_PROGRESS:
                status_packet = Packet(PacketType.STATUS)
                status_packet.data = {
                    'prog_count': sync_counter.get_prog_count(),
                    'finished_count': sync_counter.get_fin_count()
                }
                output_queue.put(
                    status_packet
                )
            elif packet.cmd == Command.SHUTDOWN:
                break
        elif packet.type == PacketType.ENCODE_TASK:
            task_queue.put(packet)
        time.sleep(1)
    print('backend: shutting down..')
    shutdown_packet = Packet(PacketType.COMMAND)
    shutdown_packet.cmd = Command.SHUTDOWN
    for i in range(0, num_workers):
        comm_queues[i].put(
            shutdown_packet
        )
    for i in range(0, num_workers):
        thread_list[i].join()


def run_interactive():
    a_queue = multiprocessing.Queue()
    b_queue = multiprocessing.Queue()
    backend_proc = Process(
        target=run_backend,
        args=(b_queue, a_queue, multiprocessing.cpu_count(),)
    )
    backend_proc.start()
    repl_routine(a_queue, b_queue)
    backend_proc.join()
    return 0


def run_batch_job(job_file):
    if not os.path.exists(job_file):
        print(
            'Failed to open {}; no such file found!'.format(
                job_file)
        )
        return -1
    a_queue = multiprocessing.Queue()
    b_queue = multiprocessing.Queue()
    job_count = 0
    with open(job_file) as in_fh:
        print(
            'Reading jobs from job file {}...'.format(job_file)
        )
        for line in in_fh:
            line_parts = line.rstrip().split(',')
            p = Packet(PacketType.ENCODE_TASK)
            p.task = EncodeTask(
                    line_parts[0],
                    line_parts[1],
                    int(line_parts[2]),
                    None,  # fps is not needed yet...
                    int(line_parts[3])
                )
            b_queue.put(p)
            job_count += 1
    print('Read in {} jobs from {}'.format(job_count, job_file))
    shutdown_packet = Packet(
        PacketType.COMMAND
    )
    shutdown_packet.cmd = Command.SHUTDOWN
    b_queue.put(
        shutdown_packet
    )
    print('Waiting for {} jobs to finish...'.format(job_count))
    backend_proc = Process(
        target=run_backend,
        args=(b_queue, a_queue, multiprocessing.cpu_count(),)
    )
    backend_proc.start()
    backend_proc.join()


def main(cmd_args):
    if cmd_args['interactive']:
        return run_interactive()
    else:
        return run_batch_job(cmd_args['job_file'])


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description=(
            'EC500 exercise 2 - async file encoding using ffmpeg'
        )
    )
    run_opt_grp = arg_parser.add_mutually_exclusive_group(
        required=True
    )
    run_opt_grp.add_argument(
        '--interactive',
        help=(
            'Run this program interactively. (Uses a REPL environment as the interface)'
        ),
        action='store_true'
    )
    run_opt_grp.add_argument(
        '-job_file',
        help=(
            'Non interactive mode; provide a list of encoding jobs to process in a CSV file'
        )
    )
    main(
        vars(arg_parser.parse_args())
    )
