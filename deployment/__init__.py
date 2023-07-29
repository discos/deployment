import sys
import os
import time
import subprocess
from argparse import Namespace
try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

DEPLOYMENT_DIR = os.path.join(os.environ['HOME'], '.deployment')
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
        ['timeout', '0.01', 'nc', '-z', ip, '22'],
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

def startVm(machine):
    if isRunning(machine):
        print(f'Machine {machine} is already running.')
        return
    else:
        sys.stdout.write(f'Starting machine {machine}')
        sys.stdout.flush()
        proc = subprocess.Popen(
            ['vagrant', 'up', machine],
            stdout=subprocess.PIPE,
            stderr=DEVNULL,
            cwd=os.path.join(os.environ['HOME'], '.deployment')
        )
        while True:
            t0 = time.time()
            code = proc.poll()
            if code is not None:
                if code == 0:
                    print('done.')
                return code
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(max(0, 1 - (time.time() - t0)))
    print('done.')

def stopVm(machine):
    if not isRunning(machine):
        print(f'Machine {machine} is not running.')
        return
    else:
        sys.stdout.write(f'Powering off machine {machine}')
        sys.stdout.flush()
        proc = subprocess.Popen(
            ['vagrant', 'halt', machine],
            stdout=subprocess.PIPE,
            stderr=DEVNULL,
            cwd=os.path.join(os.environ['HOME'], '.deployment')
        )
        while True:
            t0 = time.time()
            code = proc.poll()
            if code is not None:
                if code == 0:
                    print('done.')
                return code
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(max(0, 1 - (time.time() - t0)))
    print('done.')

def restartVm(machine):
    if isRunning(machine):
        stopVm(machine)
    startVm(machine)

def createVm(machine):
    if machine in machineList():
        if not isRunning(machine):
            startVm(machine)
    else:
        sys.stdout.write(f'Creating machine {machine}')
        sys.stdout.flush()
        proc = subprocess.Popen(
            ['vagrant', 'up', machine],
            stdout=subprocess.PIPE,
            stderr=DEVNULL,
            cwd=os.path.join(os.environ['HOME'], '.deployment')
        )
        while True:
            t0 = time.time()
            code = proc.poll()
            if code is not None:
                if code == 0:
                    print('done.')
                return code
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(max(0, 1 - (time.time() - t0)))
    return 0

def machineList(inventory='development'):
    machines = []
    if inventory == 'development':
        cmd = subprocess.Popen(
            "grep 'vb\.name' Vagrantfile | awk '{print $NF}' | sed 's/\"//g'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=DEVNULL,
            cwd=os.path.join(os.environ['HOME'], '.deployment')
        )
        vagrant_vms = [
            m.decode().strip() for m in cmd.stdout.readlines()
        ]
        cmd = subprocess.Popen(
            "vboxmanage list vms | awk '{print $1}' | sed 's/\"//g'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=DEVNULL,
        )
        vbox_vms = [
            m.decode().strip() for m in cmd.stdout.readlines()
        ]
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

def _initSSHDir(ssh_dir=os.path.join(os.environ['HOME'], '.ssh')):
    if not os.path.exists(ssh_dir):
        os.mkdir(ssh_dir, 0o700)

def generateRSAKey(
        key_file='id_rsa',
        ssh_dir=os.path.join(os.environ['HOME'], '.ssh')
    ):
    _initSSHDir(ssh_dir)
    cmd = subprocess.Popen(
        ['ssh-add', '-L'],
        stdout=subprocess.PIPE
    )
    public_key = cmd.stdout.readline().decode()
    import socket
    if os.getlogin() + '@' + socket.gethostname() not in public_key:
        file_name = os.path.join(ssh_dir, key_file)
        if not os.path.exists(file_name):
            subprocess.run(
                f"ssh-keygen -f {file_name} -t rsa -N '' -q".split()
            )

def updateKnownHosts(
        ips,
        known_hosts='known_hosts',
        ssh_dir=os.path.join(os.environ['HOME'], '.ssh')
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
    os.chmod('/tmp/ssh_askpass', 700)
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
                deployment.error(
                    f'Cannot authenticate to machine {machine}, '
                    f'try again with the correct password.'
                )
    os.remove('/tmp/ssh_askpass')
