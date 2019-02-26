# EC500 exercise 2 - Asynchronous Video Encoding
A python interactive tool which encodes multiple videos 
simultaneously using a combination of multiprocessing and
multi-threading.

## Requirements

`ffmpeg` should be found in one of your program paths on your OS. Currently you can only specify the path of 
`ffprobe` for testing. Future updates will add the ability to specify paths through a settings file. 

## Run instructions
This application has two run modes: (1) batch mode (non-interactive) and (2) interactive

To launch batch mode simple execute `python main.py -job_file <path>` where `path` is the file path to a CSV file.

The CSV file has the following format:
```
input_file_path,output_file_path,bit_rate,resolution
```

`bit_rate` is limited to `1Mbps` or `2Mbps`. Specify either option using `1` or `2` respectively.
`resolution` is limited to `480p` or `720p`. Specify either option using `480` or `720` respectively.

Example job.csv:
```
/tmp/mov.avi,/tmp/mov1.mp4,1,480
/tmp/mov.avi,/tmp/mov2.mp4,2,480
/tmp/mov.avi,/tmp/mov3.mp4,1,720
```

To run the program interactively execute `python main.py --interactive`.
The user interface is implemented through a [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) 
environment.

## Testing instructions
To run the encoder tests, simply execute `pytest`. You can specify the video path using the `--video_path` switch.
If `ffprobe` is not in your OS program path, you can specify the path to the binary using the `--ffprobe` switch.

## Measuring performance (Part 1 of assignment)
A single instance of `ffmpeg` nearly 100% of cpu usage on a dual core with 2 hardware threads per core.
Therefore, the application only assigns one ffmpeg instance per hardware thread.

![htop output](media/htop_output.png "htop output")

### TODO
1. Need to add bit_rate tests