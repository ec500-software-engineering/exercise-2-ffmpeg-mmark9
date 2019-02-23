import time
import random
import subprocess

FFMPEG_COMMAND_TEMPLATE = (
    'ffmpeg -y -i {input} -b:v {vid_bit_rate}M -s hd{res} {output}'
)


class Encode(object):

    @staticmethod
    def encode_video(encode_task):
        cmd = FFMPEG_COMMAND_TEMPLATE.format(
            input=encode_task.filename,
            output=encode_task.output_name,
            vid_bit_rate=encode_task.bit_rate_vid,
            res=encode_task.res
        )
        cmd_args = cmd.split(' ')
        proc = subprocess.Popen(
            cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        while proc.poll() is None:
            time.sleep(
                random.randint(1, 3)
            )
        return proc.returncode

