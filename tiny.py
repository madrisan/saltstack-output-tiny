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
import pprint

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
    Create generator for tiny output
    '''
    def __init__(self):
        self.colors = salt.utils.get_colors(
                __opts__.get('color'),
                __opts__.get('color_theme'))
        self.indent = 2

    def _indent(self, text):
        padding = ' ' * self.indent
        return u''.join(padding + line for line in text.splitlines(True))

    def display(self, minion_id, data):
        tinyout = []
        minion_id = sdecode(minion_id)
        color = self.colors['CYAN']   # Print the minion name in cyan
        tinyout.append((u'{0}{1}{2[ENDC]}:'
                        .format(color, minion_id, self.colors)))

        if isinstance(data, int) or isinstance(data, str):
            tinyout.append(self._indent(str(data)))
        if isinstance(data, list):
            for item in data:
                tinyout.append(self._indent(item))
        if isinstance(data, dict):
            # Verify that the needed data is present.
            # Example of valid data:
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
            data_tmp = {}
            for tname, info in six.iteritems(data):
                if isinstance(info, dict) and tname is not 'changes' \
                                      and info and '__run_num__' not in info:
                    err = (u'The State execution failed to record the order '
                           'in which all states were executed. The state '
                           'return missing data is:')
                    tinyout.insert(0, pprint.pformat(info))
                    tinyout.insert(0, err)
                if isinstance(info, dict) and 'result' in info:
                    data_tmp[tname] = info
            data = data_tmp

            issues = 0
            for block_key in sorted(
                    data,
                    key=lambda k: data[k].get('__run_num__', 0)):
                ret = data[block_key]

                changes = ret['changes']
                status = ret['result']
                diff_msg = ''

                if status is True:
                    color = self.colors['GREEN']
                    status_msg = 'ok'
                    if changes:
                        color = self.colors['CYAN']
                        status_msg += ' (changed)'
                else:
                    # status is None when __opts__['test'] has been set by user
                    color = self.colors['LIGHT_YELLOW' \
                                if status is None else 'RED']
                    status_msg = 'failed'
                    if 'comment' in ret:
                        status_msg += '\n{0}'.format(ret['comment'])
                    if 'diff' in changes:
                        diff_msg += changes['diff'].rstrip()
                    issues += 1

                comps = [sdecode(comp) for comp in block_key.split('_|-')]
                task_type = comps[0]
                task_description = comps[2].splitlines()
                if len(task_description) > 1:
                   task_description = [u'{0} [...]'.format(task_description[0])]
                tinyout.append(
                    u'{0}- ({1}) {2} ...{3}{4}{5[ENDC]}'.format(
                        ' ' * self.indent,
                        task_type,
                        task_description[0],
                        color,
                        status_msg,
                        self.colors))
                if diff_msg:
                    tinyout.append(u'{0}{1}{2[ENDC]}'.format(
                        color,
                        diff_msg,
                        self.colors))

            summary = u'{0} '.format(minion_id)
            summary += u'has {0} issue(s)'.format(issues) if issues else \
                       u'is in the required state'

            color = self.colors['RED' if issues else 'GREEN']
            tinyout.append((u'\t{0}-- {1}{2[ENDC]}'
                            .format(color, summary, self.colors)))

        return u'\n'.join(tinyout)

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
