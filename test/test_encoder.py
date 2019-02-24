import os
import json
import pytest
import subprocess
from utils import encoder
from defines.common import EncodeTask


@pytest.fixture(scope='session')
def video_path(tmpdir_factory):
    output_path = tmpdir_factory.mktemp(
        'media'
    ).join('mov.avi')
    cmd = 'ffmpeg -f lavfi -i smptebars -t 10 {}'.format(
        str(output_path)
    )
    subprocess.check_call(
        cmd.split(' ')
    )
    return output_path


def get_video_metadata(filename, ffprobe_path):
    proc_out = subprocess.Popen(
        [ffprobe_path, '-print_format', 'json',
         '-show_format', '-show_streams', filename],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.PIPE
    )
    json_raw = ''
    for line in proc_out.stdout.readlines():
        json_raw += line.decode('utf-8')
    return json.loads(json_raw)


def test_output_file_should_exist_when_encoding_finished(video_path):
    output_filename = os.path.join(
        os.path.dirname(
            os.path.realpath(video_path)
        ),
        'mov.mp4'
    )
    encoder.Encode.encode_video(
        EncodeTask(
            video_path,
            output_filename,
            1, 30, 480
        )
    )
    assert os.path.exists(
        output_filename
    ) is True


def test_input_file_should_exist_when_encoding_finished(video_path):
    output_filename = os.path.join(
        os.path.dirname(
            os.path.realpath(video_path)
        ),
        'mov.mp4'
    )
    encoder.Encode.encode_video(
        EncodeTask(
            video_path,
            output_filename,
            1, 30, 480
        )
    )
    assert os.path.exists(
        video_path
    ) is True


def test_output_video_should_have_same_length_when_encoding_finished(video_path, ffprobe_path):
    output_filename = os.path.join(
        os.path.dirname(
            os.path.realpath(video_path)
        ),
        'mov.mp4'
    )
    encoder.Encode.encode_video(
            EncodeTask(
                video_path,
                output_filename,
                1, 30, 480
            )
        )
    video_meta_in = get_video_metadata(video_path, ffprobe_path)
    video_meta_out = get_video_metadata(output_filename, ffprobe_path)
    assert int(round(float(video_meta_in['format']['duration']))) == \
           int(round(float(video_meta_out['format']['duration'])))


def test_output_video_should_be_in_mp4_container_when_encoding_is_finished(video_path, ffprobe_path):
    output_filename = os.path.join(
        os.path.dirname(
            os.path.realpath(video_path)
        ),
        'mov.mp4'
    )
    encoder.Encode.encode_video(
            EncodeTask(
                video_path,
                output_filename,
                1, 30, 480
            )
        )
    video_meta_out = get_video_metadata(output_filename, ffprobe_path)
    assert 'mp4' in video_meta_out['format']['format_name']


def test_output_video_should_have_480p_resolution_when_encoding_is_finished(video_path, ffprobe_path):
    output_filename = os.path.join(
        os.path.dirname(
            os.path.realpath(video_path)
        ),
        'mov.mp4'
    )
    encoder.Encode.encode_video(
            EncodeTask(
                video_path,
                output_filename,
                1, 30, 480
            )
        )
    video_meta_out = get_video_metadata(output_filename, ffprobe_path)
    video_width = int(video_meta_out['streams'][0]['width'])
    video_height = int(video_meta_out['streams'][0]['height'])
    assert video_height == 480 and (640 <= video_width <= 900)


def test_output_video_should_have_720p_resolution_when_encoding_is_finished(video_path, ffprobe_path):
    output_filename = os.path.join(
        os.path.dirname(
            os.path.realpath(video_path)
        ),
        'mov7.mp4'
    )
    encoder.Encode.encode_video(
            EncodeTask(
                video_path,
                output_filename,
                1, 30, 720
            )
        )
    video_meta_out = get_video_metadata(output_filename, ffprobe_path)
    video_width = int(video_meta_out['streams'][0]['width'])
    video_height = int(video_meta_out['streams'][0]['height'])
    assert video_height == 720 and video_width >= 1280


# TODO: Add bit_rate tests
#   ffprobe seems to report values less than the requested bit_rate
