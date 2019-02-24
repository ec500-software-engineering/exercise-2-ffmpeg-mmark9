import os


def pytest_addoption(parser):
    parser.addoption(
        '--ffprobe',
        action='append',
        default='ffprobe',
        help='Path to binary of ffprobe'
    )


def pytest_generate_tests(metafunc):
    if 'ffprobe_path' in metafunc.fixturenames:
        metafunc.parametrize(
            'ffprobe_path',
            (metafunc.config.getoption('ffprobe'),)
        )
