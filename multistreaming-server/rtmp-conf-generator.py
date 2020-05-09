import json
import re
import sys

#
# Configuration Templates
#

RTMP_CONF_BLOCK = """
rtmp {
    server {
        listen 1935;
        chunk_size 4096;
        notify_method get;

        application %%ENDPOINT_NAME%% {
            on_publish http://localhost/auth;
            live on;
            record all;
            record_path /var/www/html/recordings;
            record_unique on;

            # Define the applications to which the stream will be pushed, comment them out to disable the ones not needed:
            # RTMP_PUSH_DIRECTIVE_MARKER
        }

        # application defintions
        # RTMP_PUSH_BLOCK_MARKER
    }
}
"""

RTMP_PUSH_BLOCK = """
        application %%BLOCK_NAME%% {
            live on;
            record off;

            # Only allow localhost to publish
            allow publish 127.0.0.1;
            deny publish all;

            # Push URL
            push %%PUSH_URL%%;
        }

"""

RTMP_TRANSCODE_BLOCK = """
        application %%BLOCK_NAME%% {
            live on;
            record off;

            # Only allow localhost to publish
            allow publish 127.0.0.1;
            deny publish all;

            # need to transcode
            exec ffmpeg -re -i rtmp://localhost:1935/$app/$name
                -c:v libx264 -s %%PIXEL_SIZE%% -b:v %%VIDEO_BIT_RATE%% -bufsize 12M -r 30 -x264opts "keyint=%%KFS%%:min-keyint=%%KFS%%:no-scenecut:nal-hrd=cbr"
                %%AUDIO_OPTS%%
                -f flv rtmp://localhost:1935/%%DEST_BLOCK_NAME%%/$name;
        }
"""

RTMP_TRANSCODE_AUDIO_OPTS_COPY = "-c:a copy"
RTMP_TRANSCODE_AUDIO_OPTS_CUSTOM = "-c:a libfdk_aac -b:a %%AUDIO_BIT_RATE%% -ar %%AUDIO_SAMPLE_RATE%%"

PUSH_URL_YOUTUBE = "rtmp://a.rtmp.youtube.com/live2/%%STREAM_KEY%%"
PUSH_URL_FACEBOOK = "rtmp://127.0.0.1:19350/rtmp/%%STREAM_KEY%%"
PUSH_URL_TWITCH = "rtmp://live-cdg.twitch.tv/app/%%STREAM_KEY%%"
PUSH_URL_INSTAGRAM = "rtmp://127.0.0.1:19351/rtmp/%%STREAM_KEY%%"
PUSH_URL_PERISCOPE = "rtmp://%%REGION_CODE%%.pscp.tv:80/x/%%STREAM_KEY%%"
PUSH_URL_MICROSOFT_STREAM = "%%RTMP_URL%% app=live/%%APP_NAME%%"
#
#
#

def generatePlatormPushURL(block_config):
    if 'platform' not in block_config:
        print("ERROR - Application block is missing platform element.", file=sys.stderr)
        exit(1)
    push_url = 'push-it-real-good'
    if block_config['platform'] == 'youtube':
        push_url = PUSH_URL_YOUTUBE.replace('%%STREAM_KEY%%', block_config['streamKey'])
    elif block_config['platform'] == 'facebook':
        # must push through stunnel. Push through Facebook stunnel port.
        push_url = PUSH_URL_FACEBOOK.replace('%%STREAM_KEY%%', block_config['streamKey'])
    elif block_config['platform'] == 'twitch':
        push_url = PUSH_URL_TWITCH.replace('%%STREAM_KEY%%', block_config['streamKey'])
    elif block_config['platform'] == 'instagram':
        # must push through stunnel. Push through Instagram stunnel port.
        push_url = PUSH_URL_INSTAGRAM.replace('%%STREAM_KEY%%', block_config['streamKey'])
    elif block_config['platform'] == 'periscope':
        region_code = block_config['regionCode'] if 'regionCode' in block_config else 'ca'
        push_url = PUSH_URL_PERISCOPE.replace(
            '%%STREAM_KEY%%', block_config['streamKey']
        ).replace(
            '%%REGION_CODE%%', region_code
        )
    elif block_config['platform'] == 'custom':
        push_url = block_config['customRTMPURL']
    elif block_config['platform'] == 'microsoft-stream':
        ms_source_url = block_config['fullRTMPURL']
        ms_rtmp_url = re.search(r'^(.*)/live/', ms_source_url).group(1)
        ms_app_name = re.search(r'/live/(.*)$', ms_source_url).group(1)
        push_url = PUSH_URL_MICROSOFT_STREAM.replace(
                '%%RTMP_URL%%', ms_rtmp_url
            ).replace(
                '%%APP_NAME%%', ms_app_name
            )
    else:
        print("ERROR - an unsupported platform type was provided in destination configation", file=sys.stderr)
        exit(1)
    return push_url


def createRTMPApplicationBlocks(block_name, block_config):
    app_block = ''
    primary_block_name = block_name
    if 'transcode' in block_config:
        primary_block_name += '_transcoded'
        tc_conf = block_config['transcode']
        pixel_size = tc_conf['pixels'] if 'pixels' in tc_conf else '1280x720'
        video_bit_rate = tc_conf['videoBitRate'] if 'videoBitRate' in tc_conf else '4500k'
        key_frames = 30 * \
            tc_conf['videoKeyFrameSecs'] if 'videoKeyFrameSecs' in tc_conf else 60
        if ('audioBitRate' in tc_conf) or ('audioSampleRate' in tc_conf):
            audio_bit_rate = tc_conf['audioBitRate'] if 'audioBitRate' in tc_conf else '160k'
            audio_sample_rate = str(tc_conf['audioSampleRate']) if 'audioSampleRate' in tc_conf else '48000'
            audio_opts = RTMP_TRANSCODE_AUDIO_OPTS_CUSTOM.replace(
                    '%%AUDIO_BIT_RATE%%', audio_bit_rate
                ).replace(
                    '%%AUDIO_SAMPLE_RATE%%', audio_sample_rate
                    )
        else:
            audio_opts = RTMP_TRANSCODE_AUDIO_OPTS_COPY

        app_block += RTMP_TRANSCODE_BLOCK.replace(
                '%%BLOCK_NAME%%', block_name
            ).replace(
                '%%DEST_BLOCK_NAME%%', primary_block_name
            ).replace(
                '%%PIXEL_SIZE%%', pixel_size
            ).replace(
                '%%VIDEO_BIT_RATE%%', video_bit_rate
            ).replace(
                '%%KFS%%', str(key_frames)
            ).replace(
                '%%AUDIO_OPTS%%', audio_opts
            )
    app_block += RTMP_PUSH_BLOCK.replace(
            '%%BLOCK_NAME%%', primary_block_name
        ).replace(
            '%%PUSH_URL%%', generatePlatormPushURL(block_config)
        )
    return app_block


def addRTMPPushConfiguration(orig_rtmp_conf, block_config, endpoint_name):
    if 'name' not in block_config:
        print("ERROR - Application block is missing name element.", file=sys.stderr)
        exit(1)
    block_name = endpoint_name + '-' + block_config['name']
    push_pos = orig_rtmp_conf.index('            # RTMP_PUSH_DIRECTIVE_MARKER')
    rtmp_conf = orig_rtmp_conf[:push_pos] \
        + '            push rtmp://localhost/' \
        + block_name \
        + ';\n' \
        + orig_rtmp_conf[push_pos:]
    block_pos = rtmp_conf.index('        # RTMP_PUSH_BLOCK_MARKER')
    rtmp_conf = rtmp_conf[:block_pos] \
        + createRTMPApplicationBlocks(block_name, block_config) \
        + rtmp_conf[block_pos:]
    return rtmp_conf


if len(sys.argv) != 2:
    print("Must pass a single argument of the JSON configuraiton file path.", file=sys.stderr)
    sys.exit(1)

try:
    with open(sys.argv[1], 'r') as f:
        config = json.load(f)
except json.decoder.JSONDecodeError as err:
    print('ERROR decoding JSON config file "{0}": {1}'.format(sys.argv[1], err), file=sys.stderr)
    exit(1)
except:
    print('ERROR loading JSON config file "{0}"'.format(sys.argv[1]), file=sys.stderr)
    exit(1)

endpoint_name = config['endpoint'] if 'endpoint' in config else 'live'
rtmp_conf = RTMP_CONF_BLOCK.replace('%%ENDPOINT_NAME%%', endpoint_name, 1)

# unfortunate hack to make code compatible with previous spelling error
config_list_key = 'rebroacastList' if 'rebroacastList' in config else 'rebroadcastList'
for block_config in config[config_list_key]:
    rtmp_conf = addRTMPPushConfiguration(
            rtmp_conf, block_config, endpoint_name
        )

print(rtmp_conf)
