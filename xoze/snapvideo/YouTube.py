'''
Created on Oct 29, 2011

@author: ajju
'''
from xoze.snapvideo import VideoHost, Video, STREAM_QUAL_HD_720, \
    STREAM_QUAL_HD_1080, STREAM_QUAL_SD, STREAM_QUAL_LOW
from xoze.utils import http
import logging
import re
import urllib
import xbmcgui  # @UnresolvedImport

VIDEO_HOSTING_NAME = 'YouTube'

def getVideoHost():
    video_host = VideoHost()
    video_host.set_icon('http://www.automotivefinancingsystems.com/images/icons/socialmedia_youtube_256x256.png')
    video_host.set_name(VIDEO_HOSTING_NAME)
    return video_host

def retrieveVideoInfo(video_id):
    
    video_info = Video()
    video_info.set_video_host(getVideoHost())
    video_info.set_id(video_id)
    try:
        
        http.HttpClient().enable_cookies()
        video_info.set_thumb_image('http://i.ytimg.com/vi/' + video_id + '/default.jpg')
        html = http.HttpClient().get_html_content(url='http://www.youtube.com/get_video_info?video_id=' + video_id + '&asv=3&el=detailpage&hl=en_US')
        stream_map = None
        
        html = html.decode('utf8')
        html = html.replace('\n', '')
        html = html.replace('\r', '')
        html = unicode(html + '&').encode('utf-8')
        if re.search('status=fail', html):
            # XBMCInterfaceUtils.displayDialogMessage('Video info retrieval failed', 'Reason: ' + ((re.compile('reason\=(.+?)\.').findall(html))[0]).replace('+', ' ') + '.')
            logging.getLogger().info('YouTube video is removed for Id = ' + video_id + ' reason = ' + html)
            video_info.set_stopped(True)
            return video_info
        
        title = urllib.unquote_plus(re.compile('title=(.+?)&').findall(html)[0]).replace('/\+/g', ' ')
        video_info.set_name(title)
        stream_info = None
        if not re.search('url_encoded_fmt_stream_map=&', html):
            stream_info = re.compile('url_encoded_fmt_stream_map=(.+?)&').findall(html)
        stream_map = None
        if (stream_info is None or len(stream_info) == 0) and re.search('fmt_stream_map": "', html):
            stream_map = re.compile('fmt_stream_map": "(.+?)"').findall(html)[0].replace("\\/", "/")
        elif stream_info is not None:
            stream_map = stream_info[0]
            
        if stream_map is None:
            params = http.parse_url_params(html)
            logging.getLogger().debug('ENTERING live video scenario...')
            for key in params:
                logging.getLogger().debug(key + " : " + urllib.unquote_plus(params[key]))
            hlsvp = urllib.unquote_plus(params['hlsvp'])
            playlistItems = http.HttpClient().get_html_content(url=hlsvp).splitlines()
            qualityIdentified = None
            for item in playlistItems:
                logging.getLogger().debug(item)
                if item.startswith('#EXT-X-STREAM-INF'):
                    if item.endswith('1280x720'):
                        qualityIdentified = STREAM_QUAL_HD_720
                    elif item.endswith('1080'):
                        qualityIdentified = STREAM_QUAL_HD_1080
                    elif item.endswith('854x480'):
                        qualityIdentified = STREAM_QUAL_SD
                    elif item.endswith('640x360'):
                        qualityIdentified = STREAM_QUAL_LOW
                elif item.startswith('http') and qualityIdentified is not None:
                    videoUrl = http.HttpClient().add_http_cookies_to_url(item, extraExtraHeaders={'Referer':'https://www.youtube.com/watch?v=' + video_id})
                    video_info.add_stream_link(qualityIdentified, videoUrl)
                    qualityIdentified = None
            video_info.set_stopped(False)
            return video_info
        
        stream_map = urllib.unquote_plus(stream_map)
        logging.getLogger().debug(stream_map)
        formatArray = stream_map.split(',')
        for formatContent in formatArray:
            if formatContent == '':
                continue
            formatUrl = ''
            try:
                formatUrl = urllib.unquote(re.compile("url=([^&]+)").findall(formatContent)[0]) + "&title=" + urllib.quote_plus(title)   
            except Exception, e:
                logging.getLogger().error(e)     
            if re.search("rtmpe", stream_map):
                try:
                    conn = urllib.unquote(re.compile("conn=([^&]+)").findall(formatContent)[0]);
                    host = re.compile("rtmpe:\/\/([^\/]+)").findall(conn)[0];
                    stream = re.compile("stream=([^&]+)").findall(formatContent)[0];
                    path = 'videoplayback';
                    
                    formatUrl = "-r %22rtmpe:\/\/" + host + "\/" + path + "%22 -V -a %22" + path + "%22 -f %22WIN 11,3,300,268%22 -W %22http:\/\/s.ytimg.com\/yt\/swfbin\/watch_as3-vfl7aCF1A.swf%22 -p %22http:\/\/www.youtube.com\/watch?v=" + video_id + "%22 -y %22" + urllib.unquote(stream) + "%22"
                except Exception, e:
                    logging.getLogger().error(e)
            if formatUrl == '':
                continue
            logging.getLogger().debug('************************')
            logging.getLogger().debug(formatContent)
            if(formatUrl[0: 4] == "http" or formatUrl[0: 2] == "-r"):
                formatQual = re.compile("itag=([^&]+)").findall(formatContent)[0]
                if not re.search("signature=", formatUrl):
                    sig = re.compile("sig=([^&]+)").findall(formatContent)
                    if sig is not None and len(sig) == 1:
                        formatUrl += "&signature=" + sig[0]
                    else:
                        sig = re.compile("s=([^&]+)").findall(formatContent)
                        if sig is not None and len(sig) == 1:
                            formatUrl += "&signature=" + parseSignature(sig[0])
        
            qual = formatQual
            url = http.HttpClient().add_http_cookies_to_url(formatUrl, extraExtraHeaders={'Referer':'https://www.youtube.com/watch?v=' + video_id})
            logging.getLogger().debug('quality ---> ' + qual)
            if(qual == '52' or qual == '60'):  # Incorrect stream should be skipped. Causes Svere Crash
                dialog = xbmcgui.Dialog()
                dialog.ok('XBMC Unsupported codec skipped', 'YouTube has started new stream is currently cannot be decoded by XBMC player, causes crash.', 'Skipped this video quality.')
                continue
            if(qual == '13' and video_info.get_stream_link(STREAM_QUAL_LOW) is None):  # 176x144
                video_info.add_stream_link(STREAM_QUAL_LOW, url)
            elif(qual == '5' and video_info.get_stream_link(STREAM_QUAL_LOW) is None):  # 400\\327226 AUDIO ONLY
                video_info.add_stream_link(STREAM_QUAL_LOW, url)
            elif(qual == '6' and video_info.get_stream_link(STREAM_QUAL_LOW) is None):  # 640\\327360 AUDIO ONLY
                video_info.add_stream_link(STREAM_QUAL_LOW, url)
            elif(qual == '17'):  # 176x144
                video_info.add_stream_link(STREAM_QUAL_LOW, url)
            elif(qual == '18'):  # 270p/360p MP4
                video_info.add_stream_link(STREAM_QUAL_LOW, url)
            elif(qual == '22'):  # 1280x720 MP4
                video_info.add_stream_link(STREAM_QUAL_HD_720, url)
            elif(qual == '34'):  # 480x360 FLV
                video_info.add_stream_link(STREAM_QUAL_SD, url)
            elif(qual == '35' and video_info.get_stream_link(STREAM_QUAL_SD) is None):  # 854\\327480 SD
                video_info.add_stream_link(STREAM_QUAL_SD, url)
            elif(qual == '36' and video_info.get_stream_link(STREAM_QUAL_LOW) is None):  # 320x240
                video_info.add_stream_link(STREAM_QUAL_LOW, url)
            elif(qual == '37'):  # 1920x1080 MP4
                video_info.add_stream_link(STREAM_QUAL_HD_1080, url)
            elif(qual == '38' and video_info.get_stream_link(STREAM_QUAL_HD_1080) is None):  # 4096\\3272304 EPIC MP4
                video_info.add_stream_link(STREAM_QUAL_HD_1080, url)
            elif(qual == '43' and video_info.get_stream_link(STREAM_QUAL_LOW) is None):  # 360 WEBM
                video_info.add_stream_link(STREAM_QUAL_LOW, url)
            elif(qual == '44' and video_info.get_stream_link(STREAM_QUAL_SD) is None):  # 480 WEBM
                video_info.add_stream_link(STREAM_QUAL_SD, url)
            elif(qual == '45' and video_info.get_stream_link(STREAM_QUAL_HD_720) is None):  # 720 WEBM
                video_info.add_stream_link(STREAM_QUAL_HD_720, url)
            elif(qual == '46' and video_info.get_stream_link(STREAM_QUAL_HD_1080) is None):  # 1080 WEBM
                video_info.add_stream_link(STREAM_QUAL_HD_1080, url)
            elif(qual == '120'):  # New video qual
                video_info.add_stream_link(STREAM_QUAL_HD_720, url)
                # 3D streams - MP4
                # 240p -> 83
                # 360p -> 82
                # 520p -> 85
                # 720p -> 84
                # 3D streams - WebM
                # 360p -> 100
                # 360p -> 101
                # 720p -> 102
            elif video_info.get_stream_link(STREAM_QUAL_LOW) is None:  # unknown quality
                video_info.add_stream_link(STREAM_QUAL_LOW, url)

            video_info.set_stopped(False)
    except Exception, e:
        logging.getLogger().error(e)
        video_info.set_stopped(True)
    return video_info


def swap(a , b):
    c = a[0]
    a[0] = a[b % len(a)]
    a[b] = c
    return a

def parseSignature(sig):
    if len(sig) == 88:   
        sigA = list(sig)
        sigA = sigA[2:]
        sigA = swap(sigA, 1)
        sigA = swap(sigA, 10)
        sigA = list(reversed(sigA))
        sigA = sigA[2:]
        sigA = swap(sigA, 23)
        sigA = sigA[3:]
        sigA = swap(sigA, 15)
        sigA = swap(sigA, 34)
        sig = ''.join(sigA)
        return sig
    elif (len(sig) == 87):
        sigA = ''.join(list(reversed(list(sig[44: 84]))))
        sigB = ''.join(list(reversed(list(sig[3: 43]))))
        sig = sigA[21:22] + sigA[1:21] + sigA[0:1] + sigA[22:31] + sig[0:1] + sigA[32:40] + sig[43:44] + sigB
        return sig
    elif (len(sig) == 86):
        sig = sig[2:17] + sig[0:1] + sig[18:41] + sig[79:80] + sig[42:43] + sig[43:79] + sig[82:83] + sig[80:82] + sig[41:42]
        return sig
    elif (len(sig) == 85):
        sigA = ''.join(list(reversed(list(sig[44:84]))))
        sigB = ''.join(list(reversed(list(sig[3:43]))))
        sig = sigA[7:8] + sigA[1:7] + sigA[0:1] + sigA[8:23] + sig[0:1] + sigA[24:33] + sig[1:2] + sigA[34:40] + sig[43:44] + sigB
        return sig   
    elif (len(sig) == 84):
        sigA = ''.join(list(reversed(list(sig[44:84]))))
        sigB = ''.join(list(reversed(list(sig[3:43]))))
        sig = sigA + sig[43:44] + sigB[0:6] + sig[2:3] + sigB[7:16] + sigB[39:40] + sigB[17:39] + sigB[16:17]
        return sig                         
    elif (len(sig) == 83):
        sigA = ''.join(list(reversed(list(sig[43:83]))))
        sigB = ''.join(list(reversed(list(sig[2:42]))))
        sig = sigA[30:31] + sigA[1:27] + sigB[39:40] + sigA[28:30] + sigA[0:1] + sigA[31:40] + sig[42:43] + sigB[0:5] + sigA[27:28] + sigB[6:39] + sigB[5:6]
        return sig        
    elif (len(sig) == 82):
        sigA = ''.join(list(reversed(list(sig[34:82]))))
        sigB = ''.join(list(reversed(list(sig[0:33]))))
        sig = sigA[45:46] + sigA[2:14] + sigA[0:1] + sigA[15:41] + sig[33:34] + sigA[42:43] + sigA[43:44] + sigA[44:45] + sigA[41:42] + sigA[46:47] + sigB[32:33] + sigA[14:15] + sigB[0:32] + sigA[47:48]
        return sig
    else:
        return sig

def retrievePlaylistVideoItems(playlistId):
    logging.getLogger().error('YouTube Playlist ID = ' + playlistId)
    soupXml = http.HttpClient().get_beautiful_soup('http://gdata.youtube.com/feeds/api/playlists/' + playlistId + '?max-results=50')
    videoItemsList = []
    for media in soupXml.findChildren('media:player'):
        videoUrl = str(media['url'])
        videoItemsList.append(videoUrl)
    return videoItemsList
    
def retrieveReloadedPlaylistVideoItems(playlistId):
    logging.getLogger().error('YouTube Reloaded Playlist ID = ' + playlistId)
    soupXml = http.HttpClient().get_beautiful_soup('http://gdata.youtube.com/feeds/api/playlists/' + playlistId)
    videoItemsList = []
    for media in soupXml.findChildren('track'):
        videoUrl = media.findChild('location').getText()
        videoItemsList.append(videoUrl)
    return videoItemsList
    
