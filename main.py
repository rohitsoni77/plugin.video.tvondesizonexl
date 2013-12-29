'''
Created on Nov 24, 2013

@author: ajju
'''
from xoze.context import AddonContext
import logging

try:
    addon_context = AddonContext(addon_id='plugin.video.tvondesizonexl', conf={'contextFiles':['actions.xml','dr_actions.xml','dtf_actions.xml'], 'webServiceEnabled':False})
    addon_context.get_current_addon().get_action_controller().do_action('start')
    addon_context.do_clean()
    del addon_context
except Exception, e:
    logging.getLogger().exception(e)
    raise e