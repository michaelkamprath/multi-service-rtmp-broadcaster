# Multi-Service RTMP Broadcaster

The goal of this project is to create a Docker-deployed service that will allow you to easily broadcast a live stream to multiple services (YouTube, Twitch, Facebook, etc) at the same time. This stream rebroadcaster is designed to be used by a single source / user.

## Usage
The instructions here assume you are running on Linux. With some modification of the commands, you can make this Docker build work on Windows and Mac OS too.

The first step is to build the docker file. After you clone this repository, `cd` into and and issue:

```
docker build -t multistreaming-server ./multistreaming-server/
```

Once built, start the docker image on a host that has sufficient bandwidth to handle all the rebroadcasting you will do:

```
docker run -it -p 80:80 -p 1935:1935 \
  --env MULTISTREAMING_PASSWORD=__made_up_password__ \
  -v /path/to/my-rtmp-config.json:/rtmp-configuation.json
  multistreaming-server:latest
```

If this is a host than where you built the docker image, you will need to push the docker image to that host (or build it there). Alternatively, you could use the DockerHub build of this image by pulling and using the `kamprath/multistreaming-server:latest` [Docker image](https://hub.docker.com/repository/docker/kamprath/multistreaming-server). Also, if you plan on doing any transcoding when rebroadcasting a stream, you need to ensure that your docker host's CPU is sufficient for the job. It is recommend that the host CPU has at least four cores for each distinct transcoding the multi-streaming server will do. If the host CPU is not sufficient, bit rates on the transcoded streams will suffer.

Note that an environment variable is set when running the Docker image:

* `MULTISTREAMING_PASSWORD` _(REQUIRED)_ - This is a password you define and will be used by your steaming software. This is a marginally secure way to prevent other people from pushing to your stream.

You must also create and JSON file with the RTMP rebroadcasting configuration you desire. This file should get mapped from your local file system to the `/rtmp-configuation.json` file path within the Docker container. The JSON file has the following elements:

* `endpoint`- This is the name of the RTMP ingest endpoint that the source stream will be pushed to. Defaults to `live` if not specified.
* `rebroacastList`- _Required_ Contains a list of JSON objects that each configure a distinct RTMP destination that the stream pushed to the ingest endpoint will be rebroadcasted to. At least one destination should be configured. There is no specific limit on the number of destinations except for the hardware limitations of your host. Each destination is configured with the following JSON elements:
  * `name` - _Required_ A distinct label for this destination. Can be any alphanumeric string with no white space. Must be distinct from all the other destination names in this list.
  * `platform` - _Required_ The platform that this specific rebroadcast stream should be pushed to. The default RTMP destinations will be used for each platform. Supported platforms values are: `youtube`, `facebook`, `twitch`, `instagram`, `periscope`, and `custom`. Note that specifying `custom` will cause the `streamKey` element to be ignored if present and instead use the `customRTMPURL`
  * `regionCode` - If `periscope` is specified as the platform for this destination, this is the two letter region code that is part of the Periscope server URL. If undefined, it will default to `ca` (the "US West" region)
  * `streamKey` - This is the stream key that identifies the unique stream on the specified platform. This value is provided by the platform. This element must be provided for all `platform` types except for `custom`
  * `customRTMPURL` - If `custom` is specified in the `platform`, the URL specified in this element is used as-is for the destination URL.
  * `transcode` - If present, the stream will be trancoded before rebroadcasting it to this list item's destination. Note that when using this transcoding, the stream will be trancoded to 30 FPS and CBR bit rate. The value is a JSON object that contains the following configuration elements:
    * `pixels` - The pixel dimension that the stream should be transcoded to. Formatted like "1920x1080". If not specified, defaults to "1280x720".
    * `videoBitRate` - The video bit rate that should be used when sending the stream to this destination. Should be a number followed by "k" or "m" for kilo- and mega- bits-per-second. If not specified defaults to "4500k".
    * `videoKeyFrameSecs` - The number of seconds between key frames in the transcoded stream. If not specified, defaults to 2.
    * `audioCodec` - The codec that should be used for the transcoded audio signal. If not specified, defaults to `libfdk_aac`. If none of `audioCodec`, `audioBitRate` or `audioSampleRate` are specified, then the audio signal is simply copied from source with no alteration.
    * `audioBitRate` - The bit rate that should be used for the transcoded audio signal. Should be a number followed by "k" or "m" for kilo- and mega- bits-per-second. If not specified, defaults to "160k". If none of `audioCodec`, `audioBitRate` or `audioSampleRate` are specified, then the audio signal is simply copied from source with no alteration.
    * `audioSampleRate` - The sampling rate to be used for the transcoded audio signal. Should be an integer indicating the sampling Hertz. If not specified, defaults to `48000`. If none of `audioCodec`, `audioBitRate` or `audioSampleRate` are specified, then the audio signal is simply copied from source with no alteration.
  * `icecastURL` - if `icecast` is specified as the platform for this destination, this is the URL the audio stream will be pushed to. Must be in the format `icecast://username:password@hostname:port/mount`.
  * `contentType` - If `icecast` is specified as the platform for this destination, this is the content type sent to the Icecast server. Defaults to `audo/aac`.
  * `format` - If `icecast` is specified as the platform for this destination, this is the output format sent to the Icecast server. If not specified, defaults to `adts`.

Here is an example of the JSON configuraiton file:
```
{
  "endpoint": "live",
  "rebroacastList": [
    {
      "name": "youtube",
      "platform": "youtube",
      "streamKey": "abc123"
    },
    {
      "name": "facebook-1",
      "platform": "facebook",
      "streamKey": "def456",
      "transcode": {
        "pixels": "1280x720",
        "videoBitRate": "4500k"
      }
    },
    {
      "name": "facebook-2",
      "platform": "facebook",
      "streamKey": "ghi789",
      "transcode": {
        "pixels": "1280x720",
        "videoBitRate": "4500k"
      }
    },
    {
      "name": "periscope",
      "platform": "periscope",
      "regionCode": "ca",
      "streamKey": "jkl012",
      "transcode": {
        "pixels": "1280x720",
        "videoBitRate": "3500k",
        "videoKeyFrameSecs": 3,
        "audioBitRate": "128k",
        "audioSampleRate": 44100
      }
    },
    {
      "name": "icecast-1",
      "platform": "icecast",
      "icecastURL": "icecast://source:password@icecast:8000/stream"
    },
    {
      "name": "icecast-2",
      "platform": "icecast",
      "icecastURL": "icecast://source:password@icecast:8000/stream2",
      "contentType": "audio/mpeg",
      "format": "mp3",
      "transcode": {
        "audioCodec": "libmp3lame",
        "audioBitRate": "192k",
        "audioSampleRate": "44100"
      }
    }
  ]
}
```
Note that as long as the `name` elements are different, you can have more than one destination pushing to the same `platform` each with different `streamKey` values.

If you would like to capture a recording of the stream sent to the ingest endpoint, bind a local directory on your host to the `/var/www/html/recordings/` file path within the Docker image when launching the Docker container.

Once the Docker image is running, set up your stream software with the following parameters:

* **Server** : `rtmp://__docker_host_IP_address__/__endpoint_name__` - Replace `__docker_host_IP_address__` with the IP address of your host that is running this Docker container. Also replace `__endpoint_name__` with the value used for the `endpoint` element in your JSON configuration file.
* **Stream Key** : `__made_up_stream_name__?pwd=__made_up_password__` - Here `__made_up_stream_name__` is any arbitrary stream name, and `__made_up_password__` is the same password defined for `MULTISTREAMING_PASSWORD` above.

In OBS, you would set the above parameters for a "Custom..." Service in the Stream settings.

The next thing to do is start your stream!

## Future work

Goals for future improvements to this project include:

* Adding more streaming services
* Creating a useful status web page
* Create a control panel web page where you'd set stream keys rather than through a JSON file

## Acknowledgements

This work was heavily influenced by the following articles:

* The basic concept: [https://www.scaleway.com/en/docs/setup-rtmp-streaming-server/](https://www.scaleway.com/en/docs/setup-rtmp-streaming-server/)
* How to use `rtmps` with Facebook: [https://dev.to/lax/rtmps-relay-with-stunnel-12d3](https://dev.to/lax/rtmps-relay-with-stunnel-12d3)
