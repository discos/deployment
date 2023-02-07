#!/usr/bin/env python
from __future__ import print_function
import sys
import getpass
from ansible.plugins.action import ActionBase
from ansible.parsing.yaml.objects import AnsibleUnicode

__metaclass__ = type

class ActionModule(ActionBase):
    def __init__(self, task, connection, play_context, loader, templar, shared_loader_obj):
        super(ActionModule, self).__init__(task, connection, play_context, loader, templar, shared_loader_obj)

        self.setOutput(sys.stdout)
        self.setInput('/dev/tty')

    def run(self, tmp=None, task_vars=None):
        task_vars = task_vars or dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        args = self._task.args

        username = None
        if args:
            for arg in args.keys():
                if arg != 'username':
                    return self._fail(result, "Unexpected parameter '%s'." % arg)
                elif isinstance(args[arg], str):
                    username = args[arg]
                else:
                    return self._fail(result, "Parameter 'username' must be a string.")

        return self._prompt(result, username)


    def setOutput(self, outstr=None):
        self._outstr = outstr or sys.stdout


    def setInput(self, instr=None):
        self._instr = instr or '/dev/tty'


    def _prompt(self, result, username):
        # Convert to terminal input temporarily
        oldin = sys.stdin

        if isinstance(self._instr, str):
            sys.stdin = open(self._instr)
        else:
            sys.stdin = self._instr

        ask_msg = "Type user "
        confirm_msg = "Confirm user "
        if username:
            ask_msg += "'%s' " % username
            confirm_msg += "'%s' " % username
        ask_msg += "password: "
        confirm_msg += "password: "

        retries = 3
        while True:
            var = getpass.getpass(ask_msg)
            if not var:
                error_msg = "Password cannot be empty"
            elif var != getpass.getpass(confirm_msg):
                error_msg = "Typed passwords don't match"
            else:
                break
            retries -= 1
            if retries:
                print(error_msg + ", retry.\n")
            else:
                return self._fail(result, error_msg + '.')

        # Revert to previous setting
        sys.stdin = oldin

        if 'ansible_facts' not in result:
            result['ansible_facts'] = dict()

        result['ansible_facts']['typed_password'] = var

        return result


    def _fail(self, result, message, *args):
        if not isinstance(result, dict):
            raise TypeError("Invalid result provided. Expected dict, received %s." % type(result))

        if not isinstance(message, (str, AnsibleUnicode)):
            raise TypeError("Invalid message provided. Expected string, received '%s'." % type(message))

        if message == "":
            raise ValueError("Empty message provided. Requires failure message.")

        result['failed'] = True
        result['msg'] = message % (args)

        return result
