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
import BeautifulSoup
import logging
import urllib
import xbmcgui  # @UnresolvedImport


# baseURL = 'https://www.google.com/search?safe=active&isz=m&hl=en&site=imghp&tbm=isch&q='
baseURL = 'https://www.google.com/search?as_st=y&tbm=isch&hl=en&as_epq=&as_oq=&as_eq=&cr=&as_sitesearch=&safe=active&as_q={query}&q=&tbs=iar:w#as_st=y&hl=en&safe=active&tbm=isch&tbs=iar:w,isz:m'


def load_tv_show_images(req_attrib, modelMap):
    logging.getLogger().debug('load tv show image...')
    tv_show_name = req_attrib['tv-show-name']
    tv_show_url = req_attrib['tv-show-url']
    channel_type = req_attrib['channel-type']
    channel_name = req_attrib['channel-name']
    
    logging.getLogger().debug('search tv show images...' + channel_name.lower() + ' ' + tv_show_name.lower() + ' poster')
    tv_show_options = get_image(channel_name.lower() + ' ' + tv_show_name.lower() + ' poster' , tv_show_name, tv_show_url, channel_type, channel_name)
    
    modelMap['tv-show-images'] = tv_show_options
        
    
def parse_image(hsoup, tv_show_name, tv_show_url, channel_type, channel_name):
    count = 0
    tv_show_images = []
    for aTag in hsoup.findAll('a'):
        count = count + 1
        text = 'icon' + str(count)
        url = urllib.unquote(aTag['href'])
        if url.find('?') > -1:
            url = url.split('?')[1]
        params = http.parse_url_params(url)
        if not params.has_key('imgurl'):
            logging.getLogger().error(url)
            continue
        logging.getLogger().debug(params['imgurl'])
        item = xbmcgui.ListItem(label=text, iconImage=params['imgurl'], thumbnailImage=params['imgurl'])
        item.setProperty('channel-type', channel_type)
        item.setProperty('channel-name', channel_name)
        item.setProperty('tv-show-name', tv_show_name)
        item.setProperty('tv-show-url', tv_show_url)
        item.setProperty('tv-show-thumb', params['imgurl'])
        tv_show_images.append(item)
    return tv_show_images
        

def get_image(query, tv_show_name, tv_show_url, channel_type, channel_name):
    url = baseURL.format(query=urllib.quote_plus(query))
    logging.getLogger().debug('using google search : %s' % url)
    contentDiv = BeautifulSoup.SoupStrainer('ol', {'id':'rso'})
    hsoup = http.HttpClient().get_beautiful_soup(url, parseOnlyThese=contentDiv)
    try:
        return parse_image(hsoup, tv_show_name, tv_show_url, channel_type, channel_name)
    except Exception, e:
        logging.getLogger().error(e)
        return None
        
