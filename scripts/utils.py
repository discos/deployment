from __future__ import print_function
import os
import sys
import time
import subprocess
import inspect
from threading import Thread
from pexpect import pxssh
from argparse import Namespace
try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

ROOT_DIR = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]
ANSIBLE_DIR = os.path.join(ROOT_DIR, 'ansible')
INVENTORIES_DIR = os.path.join(ANSIBLE_DIR, 'inventories')

def checkPython():
    if sys.version_info[0] != 2 or sys.version_info[1] != 7:
        error('Python 2.7 is required!')

def error(msg, choices=(), name='', code=1):
    if choices:
        choices_msg = 'Allowed values of {}:\n'.format(name)
    else:
        choices_msg = ''
    print('ERROR: {}{}'.format(msg, choices_msg), file=sys.stderr)
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
        print('\n{}'.format(doc), file=sys.stderr)
    sys.exit(code)

def getInventories():
    inventories = []
    for item in os.listdir(INVENTORIES_DIR):
        if not os.path.isfile(os.path.join(INVENTORIES_DIR, item)):
            inventories.append(item)
    return inventories

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
    clusters = hosts.keys() + groups.keys()
    return hosts, groups, clusters 

def sshCommand(ssh, command):
    rc = 0
    output = ''
    try:
        ssh.sendline(command)
        while not ssh.prompt():
            time.sleep(0.05)
        output = ssh.before.split('\r\n')[1:-1]
        ssh.sendline('echo $?')
        while not ssh.prompt():
            time.sleep(0.05)
        rc = not bool(int(ssh.before.split('\r\n')[1:-1][0]))
    except pexpect.exceptions.EOF:
        pass
    return Namespace(rc=rc, stdout=output)

def sshLogin(ip, password=None):
    try:
        ssh = pxssh.pxssh(timeout=0.2)
        if not password:
            ssh.login(ip, 'root')
        else:
            ssh.login(ip, 'root', password)
        sshCommand(ssh, 'unset HISTFILE')
        return ssh
    except pxssh.ExceptionPxssh:
        return None

def ping(ip):
    rc = subprocess.call(
        ['timeout', '0.5', 'ping', '-c', '1', '-i', '0.2', ip],
        shell=False,
        stdout=DEVNULL
    )
    if rc == 0:
        return True
    return False

def getIp(machine, inventory='development'):
    hosts, _, _ = parseInventory(inventory)
    try:
        return hosts[machine]['ip']
    except KeyError:
        return None

def _startVm(machine):
    machine_id = 'discos_{}'.format(machine)
    subprocess.call(
        ['VBoxManage', 'startvm', machine_id, '--type', 'headless'],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    ip = getIp(machine)
    state = 0
    while state >= 0:
        if state == 0:
            if ping(ip):
                state = 1
        elif state == 1:
            ssh = sshLogin(ip, 'vagrant')
            if ssh:
                ssh.logout()
                state = -1
        time.sleep(0.5)
    return

def startVm(machine):
    if machineState(machine) == 'running':
        print('Machine {} is already running.'.format(machine))
        return
    sys.stdout.write('Starting machine {}'.format(machine))
    sys.stdout.flush()
    t = Thread(target=_startVm, args=(machine,))
    t.start()
    while t.isAlive():
        t0 = time.time()
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(max(0, 1 - (time.time() - t0)))
    print('done.')

def _stopVm(machine):
    ip = getIp(machine)
    state = 0
    while state >= 0:
        if state == 0:
            if ping(ip):
                state = 1
        elif state == 1:
            ssh = sshLogin(ip, 'vagrant')
            if ssh:
                sshCommand(ssh, 'shutdown -P now')
                ssh.logout()
                state = 2
        elif state == 2:
            if machineState(machine) == 'powered off':
                state = -1
        time.sleep(0.5)
    return

def stopVm(machine):
    if machineState(machine) == 'powered off':
        print('Machine {} is not running.'.format(machine))
        return
    sys.stdout.write('Powering off machine {}'.format(machine))
    sys.stdout.flush()
    t = Thread(target=_stopVm, args=(machine,))
    t.start()
    while t.isAlive():
        t0 = time.time()
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(max(0, 1 - (time.time() - t0)))
    print('done.')

def _restartVm(machine):
    ip = getIp(machine)
    state = 0
    while state >= 0:
        if state == 0:
            if ping(ip):
                state = 1
        elif state == 1:
            ssh = sshLogin(ip, 'vagrant')
            if ssh:
                sshCommand(ssh, 'reboot now')
                ssh.logout()
                state = 2
        elif state == 2:
            if not ping(ip):
                state = 3
        elif state == 3:
            if ping(ip):
                state = 4
        elif state == 4:
            ssh = sshLogin(ip, 'vagrant')
            if ssh:
                ssh.logout()
                state = -1
        time.sleep(0.5)
    return

def restartVm(machine):
    if machineState(machine) == 'powered off':
        startVm(machine)
        return
    sys.stdout.write('Restarting machine {}'.format(machine))
    sys.stdout.flush()
    t = Thread(target=_restartVm, args=(machine,))
    t.start()
    while t.isAlive():
        t0 = time.time()
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(max(0, 1 - (time.time() - t0)))
    print('done.')

def createVm(machine):
    if machine in machineList():
        if machineState(machine) == 'powered off':
            startVm(machine)
    else:
        sys.stdout.write('Creating machine {}'.format(machine))
        sys.stdout.flush()
        proc = subprocess.Popen(
            ['vagrant', 'up', machine],
            stdout=subprocess.PIPE,
            stderr=DEVNULL
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

def vagrantList():
    machines = []
    for line in open(os.path.join(ROOT_DIR, 'Vagrantfile'), 'r'):
        if 'config.vm.define' in line:
            machines.append(line.split()[1].strip('"'))
    return machines

def machineList():
    cmd = subprocess.Popen(
        'VBoxManage list vms'.split(),
        stdout=subprocess.PIPE
    )
    machines = []
    for line in cmd.stdout:
        m_name = line.split()[0].strip('"').replace('discos_', '')
        machines.append(m_name)
    return machines

def machineState(name):
    if name not in machineList():
        error('Machine {} unknown!'.format(name))
    m_id = 'discos_{}'.format(name)
    cmd = subprocess.Popen(
        ['VBoxManage', 'showvminfo', m_id],
        stdout=subprocess.PIPE,
        stderr=DEVNULL
    )
    cmd.wait()
    state = None
    for line in cmd.stdout:
        if 'State' in line:
            state = ' '.join(line.strip().split()[1:-2])
    return state

def _initSSHDir(ssh_dir=os.path.join(os.environ['HOME'], '.ssh')):
    if not os.path.exists(ssh_dir):
        os.mkdir(ssh_dir, 0o700)

def getRSAKey(
        key_file='id_rsa',
        ssh_dir=os.path.join(os.environ['HOME'], '.ssh')
    ):
    _initSSHDir(ssh_dir)
    file_name = os.path.join(ssh_dir, key_file)
    if not os.path.exists(file_name):
        subprocess.call(
            "ssh-keygen -f {} -t rsa -N '' -q".format(file_name),
            shell=True
        )
    public_key = open(file_name + '.pub').read().strip()
    return public_key

def updateKnownHosts(
        ips,
        known_hosts='known_hosts',
        ssh_dir=os.path.join(os.environ['HOME'], '.ssh')
    ):
    _initSSHDir(ssh_dir)
    file_name = os.path.join(ssh_dir, known_hosts)
    for ip in ips:
        subprocess.call(
            ['ssh-keygen', '-R', ip],
            shell=False,
            stdout=DEVNULL,
            stderr=DEVNULL
        )
        subprocess.call(
            ['ssh-keyscan', '-H', ip],
            shell=False,
            stderr=DEVNULL,
            stdout=open(file_name, 'a')
        )

def detachFromNM(ssh, interface):
    sshCommand(
        ssh,
        """sed -i -e 's/NM_CONTROLLED="yes"/NM_CONTROLLED="no"/g'"""
        + """ /etc/sysconfig/network-scripts/ifcfg-%s""" % interface
    )

def authorizeKey(ssh, public_key):
    sshCommand(ssh, 'usermod -m -d /vagrant vagrant')
    sshCommand(ssh, 'mkdir .ssh')
    sshCommand(ssh, 'chmod 0700 .ssh')
    auth_file = sshCommand(ssh, 'cat .ssh/authorized_keys')
    found = False
    if auth_file.rc:
        for line in auth_file.stdout:
            if public_key in line:
                found = True
    if not auth_file.rc or not found:
        sshCommand(
            ssh,
            'echo "{}" >> .ssh/authorized_keys'.format(public_key)
        )
        sshCommand(ssh, 'chmod 0600 .ssh/authorized_keys')
