'''
Created on Nov 24, 2013

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
from xoze.context import AddonContext
import logging

def start_addon(req_attrib, modelMap):
    logging.getLogger().debug('Hello ***********************')
    logging.getLogger().debug(req_attrib)
    
def check_wish(req_attrib, modelMap):
    logging.getLogger().debug('Wish needed ***********************')
    
    logging.getLogger().debug('Wish settings = %s' % AddonContext().get_addon().getSetting('wishDisplayed'))
    displayedCounter = AddonContext().get_addon().getSetting('wishDisplayed')
    if displayedCounter == '' or displayedCounter == 'hide':
        return 'redirect:determineSource'
    
def display_wish(req_attrib, modelMap):
    logging.getLogger().debug('Wish needed ***********************')
    displayedCounter = int(AddonContext().get_addon().getSetting('wishDisplayed'))
    modelMap['displayedCounter'] = displayedCounter
    
def determine_source(req_attrib, modelMap):
    sourceChosen = int(AddonContext().get_addon().getSetting('tvShowsSource'))
    if sourceChosen == 0:
        return 'redirect:dr-checkCache'
    elif sourceChosen == 1:
        return 'redirect:dtf-checkCache'
    
def end_addon(req_attrib, modelMap):
    logging.getLogger().debug('BYE bye ***********************')
    logging.getLogger().debug(req_attrib)
