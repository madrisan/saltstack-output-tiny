# -*- coding: utf-8 -*-
'''
Outputter for displaying results of state runs the most succint way
===================================================================

The tiny outputter has been developed to make the output from shell
commands on minions appear very short but with all the informations
on configuration changes and failures.
'''

# Import python libs
from __future__ import absolute_import
from __future__ import print_function
import logging

# Import salt libs
import salt.utils
from salt.utils.locales import sdecode

# Import 3rd-party libs
import salt.ext.six as six

log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'tiny'

def __virtual__():
    return __virtualname__

class TinyDisplay(object):
    '''
    Create generator for tiyn output
    '''
    def __init__(self):
        self.colors = salt.utils.get_colors(
                __opts__.get('color'),
                __opts__.get('color_theme'))
        self.indent = 2

    def display(self, minion_id, data):
        # Example of data:
        # {
        #   "frghcslsgwv01": {
        #     "file_|-/etc/salt/roster_|-/etc/salt/roster_|-managed": {
        #       "comment": "File /etc/salt/roster is in the correct state",
        #       "pchanges": {},
        #       "name": "/etc/salt/roster",
        #       "start_time": "14:49:50.431497",
        #       "result": true,
        #       "duration": 3.563,
        #       "__run_num__": 4,
        #       "changes": {},
        #       "__id__": "/etc/salt/roster"
        #     },
        #     ...

        minion_id = sdecode(minion_id)

        color = self.colors['CYAN']   # Print the minion name in cyan
        tiny_data = '{0}{1}{2[ENDC]}\n'.format(color, minion_id, self.colors)

        issues = 0
        for block_key in sorted(
                data,
                key=lambda k: data[k].get('__run_num__', 0)):
            ret = data[block_key]

            changes = ret['changes']
            status = ret['result']  # FIXME: status can be None

            if changes:
                color = self.colors['CYAN']
                status_msg = 'ok (changed)'
            elif status:
                color = self.colors['GREEN']
                status_msg = 'ok'
            else:
                color = self.colors['RED']
                status_msg = 'ko'

            if status is False:
                issues += 1

            comps = [sdecode(comp) for comp in block_key.split('_|-')]

            tiny_data += '{0}{1}- ({2}) {3} ... {4}{5[ENDC]}\n'.format(
                         color,
                         ' ' * self.indent,
                         comps[0],
                         comps[2],
                         status_msg,
                         self.colors)

        summary = '{0} '.format(minion_id)
        summary += 'has {0} issue(s)'.format(issues) if issues else \
                   'is in the required state'

        color = self.colors['RED' if issues else 'GREEN']
        tiny_data += '\t{0}-- {1}{2[ENDC]}'.format(color, summary, self.colors)
        return tiny_data

def output(data, **kwargs):  # pylint: disable=unused-argument
    '''
    Print the output data in the most succint way.
    '''
    tiny = TinyDisplay()
    ret = [
        tiny.display(minion_id, minion_data)
            for minion_id, minion_data in six.iteritems(data)
    ]
    if ret:
        return "\n".join(ret)
    log.error(
        'Data passed to ' + __virtualname__ + ' outputter is invalid: %s',
        data
    )
    # We should not reach here, but if we do return empty string
    return ''
