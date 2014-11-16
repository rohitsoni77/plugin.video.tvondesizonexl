'''
Created on Jan 2, 2014

@author: ajdeveloped@gmail.com

This file is part of XOZE. 

XOZE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

XOZE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with XOZE.  If not, see <http://www.gnu.org/licenses/>.
'''
from xoze.utils import http
import logging
import urllib
import xbmcgui  # @UnresolvedImport
try:
    import json
except ImportError:
    import simplejson as json


# baseURL = 'https://www.google.com/search?safe=active&isz=m&hl=en&site=imghp&tbm=isch&q='
# baseURL = 'https://www.google.com/search?as_st=y&tbm=isch&hl=en&as_epq=&as_oq=&as_eq=&cr=&sitesearch=&safe=active&q={query}'
baseURL = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q={query}'


def load_tv_show_images(req_attrib, modelMap):
    logging.getLogger().debug('load tv show image...')
    tv_show_name = req_attrib['tv-show-name']
    tv_show_url = req_attrib['tv-show-url']
    channel_type = req_attrib['channel-type']
    channel_name = req_attrib['channel-name']
    
    logging.getLogger().debug('search tv show images...' + channel_name.lower() + ' ' + tv_show_name.lower() + ' poster')
    tv_show_options = get_image(channel_name.lower() + ' ' + tv_show_name.lower() + ' poster' , tv_show_name, tv_show_url, channel_type, channel_name)
    
    modelMap['tv-show-images'] = tv_show_options
        
    
def parse_image(results, tv_show_name, tv_show_url, channel_type, channel_name):
    count = 0
    tv_show_images = []
    
    for image_info in results:
        url = image_info['unescapedUrl']
        # Remove file-system path characters from name.
        title = image_info['titleNoFormatting'].replace('/', '').replace('\\', '')
        count = count + 1
#         text = 'icon' + str(count)
        
        logging.getLogger().debug(url)
        item = xbmcgui.ListItem(label=title, iconImage=url, thumbnailImage=url)
        item.setProperty('channel-type', channel_type)
        item.setProperty('channel-name', channel_name)
        item.setProperty('tv-show-name', tv_show_name)
        item.setProperty('tv-show-url', tv_show_url)
        item.setProperty('tv-show-thumb', url)
        tv_show_images.append(item)
    return tv_show_images
        

def get_image(query, tv_show_name, tv_show_url, channel_type, channel_name):
    url = baseURL.format(query=urllib.quote_plus(query))
    logging.getLogger().debug('using google search : %s' % url)
    html = http.HttpClient().get_html_content(url)
    results = json.loads(html)['responseData']['results']
    try:
        return parse_image(results, tv_show_name, tv_show_url, channel_type, channel_name)
    except Exception, e:
        logging.getLogger().error(e)
        return None
        
