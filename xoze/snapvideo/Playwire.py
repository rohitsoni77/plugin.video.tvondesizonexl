'''
Created on Nov 21, 2012

@author: ajju
'''
from xoze.snapvideo import VideoHost, Video, STREAM_QUAL_HD_720
from xoze.utils import http
import logging
import re
try:
    import json
except ImportError:
    import simplejson as json

VIDEO_HOSTING_NAME = 'PLAYWIRE'

def getVideoHost():
    video_host = VideoHost()
    video_host.set_icon('http://www.playwire.com/images/logo.png')
    video_host.set_name(VIDEO_HOSTING_NAME)
    return video_host


def retrieveVideoInfo(video_id):
    video = Video()
    video.set_video_host(getVideoHost())
    video.set_id(video_id)
    try:
        video_link = 'http://cdn.playwire.com/' + str(video_id) + '.json'
        
        html = http.HttpClient().get_html_content(url=video_link)
        jsonObj = json.loads(html)
        logging.getLogger().debug(jsonObj)
        img_link = str(jsonObj['poster'])
        video_link = str(jsonObj['src'])
        
        video.set_stopped(False)
        video.set_thumb_image(img_link)
        video.set_name("PLAYWIRE Video")
        if re.search(r'\Artmp', video_link):
            video.add_stream_link(STREAM_QUAL_HD_720, video_link)
        else:
            video.add_stream_link(STREAM_QUAL_HD_720, video_link)
    except:
        video.set_stopped(True)
    return video

