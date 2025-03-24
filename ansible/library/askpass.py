#!/usr/bin/python
import crypt
import getpass
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type


def run_module():
    module_args = dict(username=dict(type='str', required=True))
    result = dict(changed=False, password_hash=None)

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    ask_msg = f"Type user {module.params['username']} password:"
    confirm_msg = f"Confirm user {module.params['username']} password:"

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
            module.fail_json(msg=error_msg + '.', **result)

    result['password_hash'] = crypt.crypt(var, f"$6$rounds=656000${module.params['username'][:8]}$")
    result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
