import sys
import os
import time
import subprocess
from argparse import Namespace
try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

DEPLOYMENT_DIR = os.path.join(os.environ.get('HOME'), '.deployment')
ANSIBLE_DIR = os.path.join(DEPLOYMENT_DIR, 'ansible')
INVENTORIES_DIR = os.path.join(ANSIBLE_DIR, 'inventories')
os.environ['ANSIBLE_CONFIG'] = os.path.join(ANSIBLE_DIR, 'ansible.cfg')

def error(msg, choices=(), name='', code=1):
    import inspect
    choices_msg = ''
    if choices:
        if len(msg) > 0:
            choices_msg = ' '
        choices_msg += f'Allowed values of {name}:\n'
    print(f'ERROR: {msg}{choices_msg}', file=sys.stderr)
    if choices:
        for choice in choices:
            print(' '*2, choice, file=sys.stderr)
    caller_module = None
    stack = 1
    while True:
        caller_module = inspect.getmodule(inspect.stack()[stack][0])
        if caller_module != sys.modules[__name__]:
            break
        stack += 1
    doc = caller_module.__doc__
    if doc:
        print(f'\n{doc}', file=sys.stderr)
    sys.exit(code)

def getEnvironments():
    inventories = {}
    systems = []
    for env in os.listdir(INVENTORIES_DIR):
        if not os.path.isfile(os.path.join(INVENTORIES_DIR, env)):
            h, g, c = parseInventory(env)
            inventories[env] = {}
            inventories[env]['hosts'] = h
            inventories[env]['groups'] = g
            inventories[env]['clusters'] = c

            for cluster in c:
                systems.append(f'{cluster}:{env}')
    return (inventories, systems)

def parseInventory(inventory):
    hosts = {}
    groups = {}
    clusters = []
    hosts_file = os.path.join(INVENTORIES_DIR, inventory, 'hosts')
    with open(hosts_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            if '[' in line and ']' in line:
                if ':' not in line:
                    # Group line
                    current_group = line[line.find('[')+1:line.find(']')]
                else:
                    # Cluster line
                    current_group = line[line.find('[')+1:line.find(':')]
                    groups[current_group] = []
            elif 'ansible_host' in line:
                # Host line
                hostname, ansible_host = line.split()
                _ ,ansible_host = ansible_host.split('=')
                host = {}
                host['hostname'] = hostname
                host['ip'] = ansible_host            
                hosts[current_group] = host
            elif line != '\n' and current_group:
                # Inside cluster
                host = line.strip()
                if host in hosts.keys():
                    groups[current_group].append(line.strip())
                elif host in groups.keys():
                    for machine in groups[host]:
                        if machine not in groups[current_group]:
                            groups[current_group].append(machine)
    clusters = list(hosts.keys()) + list(groups.keys())
    return hosts, groups, clusters 

def getBranches():
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    import json
    branches = []
    try:
        request = Request(
            'https://api.github.com/repos/discos/discos/branches'
        )
        branches += json.loads(urlopen(request).read())
        request = Request(
            'https://api.github.com/repos/discos/discos/tags'
        )
        branches += json.loads(urlopen(request).read())
        branches = [str(item.get('name')) for item in branches]
        branches.sort()
    except HTTPError:
        pass
    return branches

def sshLogin(ip, user='root'):
    sp = subprocess.run(
        [
            'timeout',
            '2' if os.environ.get('CI') else '0.5',
            'ssh',
            f'{user}@{ip}',
            '-o',
            'PasswordAuthentication=false',
            '"exit"'
        ],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    if sp.returncode == 0:
        return True
    else:
        return False

def ping(ip):
    sp = subprocess.run(
        [
            'timeout',
            '1' if os.environ.get('CI') else '0.1',
            'nc',
            '-z',
            ip,
            '22'
        ],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    if sp.returncode == 0:
        return True
    else:
        return False

def getIp(machine, inventory='development'):
    hosts, _, _ = parseInventory(inventory)
    try:
        return hosts[machine]['ip']
    except KeyError:
        error(f'No IP associated with machine {machine}!')

def statusVm(machine):
    return_code = 0
    if machine not in _vagrantList():
        print(f'Machine {machine} unknown.')
        return_code = 1
    elif machine not in machineList():
        print(f'Machine {machine} not created.')
    elif isRunning(machine):
        print(f'Machine {machine} is running.')
    else:
        print(f'Machine {machine} powered off.')
    return return_code 

def startVm(machine):
    return_code = 0
    if machine not in _vagrantList():
        print(f'Machine {machine} unknown.')
        return_code = 1
    elif machine not in machineList():
        print(f'Machine {machine} not created.')
        return_code = 2
    elif isRunning(machine):
        print(f'Machine {machine} is already running.')
    else:
        sys.stdout.write(f'Starting machine {machine}')
        sys.stdout.flush()
        cmd = subprocess.Popen(
            ['vagrant', 'up', machine],
            stdout=subprocess.PIPE,
            stderr=DEVNULL,
            cwd=os.path.join(os.environ.get('HOME'), '.deployment')
        )
        while True:
            t0 = time.time()
            code = cmd.poll()
            if code is not None:
                if code == 0:
                    print('done.')
                else:
                    print('error while starting the requested VM.')
                    return_code = 3
                sys.stdout.flush()
                break
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(max(0, 1 - (time.time() - t0)))
    return return_code

def stopVm(machine):
    return_code = 0
    if machine not in _vagrantList():
        print(f'Machine {machine} unknown.')
        return_code = 1
    elif machine not in machineList():
        print(f'Machine {machine} not created.')
        return_code = 2
    elif not isRunning(machine):
        print(f'Machine {machine} is not running.')
    else:
        sys.stdout.write(f'Powering off machine {machine}')
        sys.stdout.flush()
        cmd = subprocess.Popen(
            ['vagrant', 'halt', machine],
            stdout=subprocess.PIPE,
            stderr=DEVNULL,
            cwd=os.path.join(os.environ.get('HOME'), '.deployment')
        )
        while True:
            t0 = time.time()
            code = cmd.poll()
            if code is not None:
                if code == 0:
                    print('done.')
                else:
                    print('error while stopping the requested VM.')
                    return_code = 3
                sys.stdout.flush()
                break
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(max(0, 1 - (time.time() - t0)))
    return return_code

def restartVm(machine):
    if isRunning(machine):
        stopVm(machine)
    startVm(machine)

def createVm(machine):
    return_code = 0
    if machine not in _vagrantList():
        print(f'Machine {machine} unknown.')
        return_code = 1
    elif machine in machineList():
        print(f'Machine {machine} already created.')
        return_code = 2
    else:
        sys.stdout.write(f'Creating machine {machine}')
        sys.stdout.flush()
        cmd = subprocess.Popen(
            ['vagrant', 'up', machine],
            stdout=DEVNULL,
            stderr=DEVNULL,
            cwd=os.path.join(os.environ.get('HOME'), '.deployment')
        )
        while True:
            t0 = time.time()
            code = cmd.poll()
            if code is not None:
                if code == 0:
                    print('done.')
                else:
                    print('error while creating the requested VM.')
                    return_code = 3
                sys.stdout.flush()
                break
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(max(0, 1 - (time.time() - t0)))
    return return_code

def destroyVm(machine):
    return_code = 0
    if machine not in _vagrantList():
        print(f'Machine {machine} unknown.')
        return_code = 1
    elif machine not in machineList():
        print(f'Machine {machine} not created.')
    else:
        valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
        prompted = 0
        choice = False
        while True:
            if prompted == 3:
                return return_code
            prompted += 1
            sys.stdout.write(
                f'Are you sure you want to destroy machine {machine}? [y/N]: '
            )
            sys.stdout.flush()
            choice = input().lower()
            if choice not in valid.keys():
                continue
            else:
                choice = False if choice == '' else valid[choice]
                break
        if choice == False:
            return return_code
        sys.stdout.write(f'Destroying machine {machine}')
        sys.stdout.flush()
        cmd = subprocess.Popen(
            ['vagrant', 'destroy', '-f', machine],
            stdout=DEVNULL,
            stderr=DEVNULL,
            cwd=os.path.join(os.environ.get('HOME'), '.deployment')
        )
        while True:
            t0 = time.time()
            code = cmd.poll()
            if code is not None:
                if code == 0:
                    print('done.')
                else:
                    print('error while destroying the requested VM.')
                    return_code = 3
                sys.stdout.flush()
                break
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(max(0, 1 - (time.time() - t0)))
    return return_code

def exportVm(machine, outdir=os.environ.get('HOME')):
    return_code = 0
    if machine not in _vagrantList():
        print(f'Machine {machine} unknown.')
        return_code = 1
    elif machine not in machineList():
        print(f'Machine {machine} not created.')
        return_code = 2
    elif isRunning(machine):
        print(f'Machine {machine} is running. Stop it and try again.')
        return_code = 3
    else:
        outfile = os.path.join(outdir, f'discos_{machine}.ova')
        sys.stdout.write(f'Exporting machine {machine} as {outfile}')
        sys.stdout.flush()
        cmd = subprocess.Popen(
            ['vboxmanage', 'export', f'discos_{machine}', '-o', outfile],
            stdout=DEVNULL,
            stderr=DEVNULL
        )
        while True:
            t0 = time.time()
            code = cmd.poll()
            if code is not None:
                if code == 0:
                    print('done.')
                else:
                    print('error while exporting the requested VM.')
                    return_code = code
                sys.stdout.flush()
                break
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(max(0, 1 - (time.time() - t0)))
    return return_code

def _vagrantList():
    cmd = subprocess.Popen(
        "grep 'vb\.name' Vagrantfile | awk '{print $NF}' | sed 's/\"//g'",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=DEVNULL,
        cwd=os.path.join(os.environ.get('HOME'), '.deployment')
    )
    machines = cmd.stdout.readlines()
    return [m.decode().strip().replace('discos_', '') for m in machines]

def _vboxList():
    cmd = subprocess.Popen(
        "vboxmanage list vms | awk '{print $1}' | sed 's/\"//g'",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=DEVNULL,
    )
    machines = cmd.stdout.readlines()
    return [m.decode().strip().replace('discos_', '') for m in machines]

def machineList(inventory='development'):
    machines = []
    if inventory == 'development':
        vagrant_vms = _vagrantList()
        vbox_vms = _vboxList()
        machines = [
            m.replace('discos_', '') for m in vagrant_vms if m in vbox_vms
        ]
    else:
        h, _, _ = parseInventory(inventory)
        machines = h.keys()
    return machines

def isRunning(name, inventory='development'):
    if name not in machineList():
        error(f'Machine {name} unknown!')
    return ping(getIp(name, inventory))

def _initSSHDir(ssh_dir=os.path.join(os.environ.get('HOME'), '.ssh')):
    if not os.path.exists(ssh_dir):
        os.mkdir(ssh_dir, 0o700)

def generateRSAKey(
        key_file='id_rsa',
        ssh_dir=os.path.join(os.environ.get('HOME'), '.ssh')
    ):
    file_name = os.path.join(ssh_dir, key_file)
    _initSSHDir(ssh_dir)
    cmd = subprocess.Popen(
        ['ssh-add', '-L'],
        stdout=subprocess.PIPE
    )
    public_key = cmd.stdout.readline().decode()
    import socket
    if os.getlogin() + '@' + socket.gethostname() not in public_key:
        if not os.path.exists(file_name):
            subprocess.run(
                f"ssh-keygen -q -f {file_name} -t rsa -P ''",
                stdout=DEVNULL,
                stderr=DEVNULL,
                shell=True
            )
    subprocess.call(
        ['ssh-add', f'{file_name}'],
        stdout=DEVNULL,
        stderr=DEVNULL
    )

def updateKnownHosts(
        ips,
        known_hosts='known_hosts',
        ssh_dir=os.path.join(os.environ.get('HOME'), '.ssh')
    ):
    _initSSHDir(ssh_dir)
    file_name = os.path.join(ssh_dir, known_hosts)
    for ip in ips:
        subprocess.run(
            ['ssh-keygen', '-R', ip],
            stdout=DEVNULL,
            stderr=DEVNULL
        )
        subprocess.run(
            ['ssh-keyscan', '-t', 'rsa', '-H', ip],
            stderr=DEVNULL,
            stdout=open(file_name, 'a')
        )

def authorizeKey(ip):
    subprocess.call(
        ['setsid', 'ssh-copy-id', f'root@{ip}'],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )

def injectRSAKey(machines):
    import getpass
    with open('/tmp/ssh_askpass', 'w') as f:
        f.write('#!/bin/bash\necho $DEPLOY_PASSWORD\n')
    os.chmod('/tmp/ssh_askpass', 0o700)
    os.environ['SSH_ASKPASS'] = '/tmp/ssh_askpass'
    for machine, ip in machines.items():
        if not sshLogin(ip):
            # Cannot authenticate, we need to exchange the public key
            os.environ['DEPLOY_PASSWORD'] = getpass.getpass(
                f"Type the password for user 'root' on machine {machine}: "
            )
            authorizeKey(ip)
            os.unsetenv('DEPLOY_PASSWORD')
            if not sshLogin(ip):
                error(
                    f'Cannot authenticate to machine {machine}, '
                    f'try again with the correct password.'
                )
    os.remove('/tmp/ssh_askpass')
