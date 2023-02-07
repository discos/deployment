from __future__ import print_function
import sys
import inspect

def error(msg, choices=(), name='', code=1):
    choices_msg = ''
    if choices:
        if len(msg) > 0:
            choices_msg = ' '
        choices_msg += 'Allowed values of {}:\n'.format(name)
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

import os
import time
import subprocess
import pexpect
from threading import Thread
from pexpect import pxssh
from argparse import Namespace
from multiprocessing import Process
try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

DEPLOYMENT_DIR = os.path.join(os.environ['HOME'], '.deployment')
ANSIBLE_DIR = os.path.join(DEPLOYMENT_DIR, 'ansible')
INVENTORIES_DIR = os.path.join(ANSIBLE_DIR, 'inventories')
os.environ['ANSIBLE_CONFIG'] = os.path.join(ANSIBLE_DIR, 'ansible.cfg')

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
    clusters = list(hosts.keys()) + list(groups.keys())
    return hosts, groups, clusters 

def sshCommand(ssh, command):
    rc = 0
    output = ''
    try:
        ssh.sendline(command)
        while not ssh.prompt():
            time.sleep(0.05)
        output = ssh.before.decode().split('\r\n')[1:-1]
        ssh.sendline('echo $?')
        while not ssh.prompt():
            time.sleep(0.05)
        rc = not bool(int(ssh.before.decode().split('\r\n')[1:-1][0]))
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
    def loginTry(ip):
        try:
            ssh = pxssh.pxssh()
            ssh.login(ip, 'root')
            ssh.logout()
        except pxssh.ExceptionPxssh as err:
            if str(err) == 'Could not establish connection to host':
                time.sleep(4)

    p = Process(target=loginTry, args=(ip,))
    p.start()
    p.join(3)
    if p.is_alive():
        p.terminate()
        return False
    return True

def getIp(machine, inventory='development'):
    hosts, _, _ = parseInventory(inventory)
    try:
        return hosts[machine]['ip']
    except KeyError:
        error('No IP associated with machine {}!'.format(machine))

def _startVm(machine):
    machine_id = 'discos_{}'.format(machine)
    ip = getIp(machine)
    subprocess.call(
        ['VBoxManage', 'startvm', machine_id, '--type', 'headless'],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
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
    if isRunning(machine):
        print('Machine {} is already running.'.format(machine))
        return
    sys.stdout.write('Starting machine {}'.format(machine))
    sys.stdout.flush()
    t = Thread(target=_startVm, args=(machine,))
    t.start()
    while t.is_alive():
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
            if not isRunning(machine):
                state = -1
        time.sleep(0.5)
    return

def stopVm(machine):
    if not isRunning(machine):
        print('Machine {} is not running.'.format(machine))
        return
    sys.stdout.write('Powering off machine {}'.format(machine))
    sys.stdout.flush()
    t = Thread(target=_stopVm, args=(machine,))
    t.start()
    while t.is_alive():
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
    if not isRunning(machine):
        startVm(machine)
        return
    sys.stdout.write('Restarting machine {}'.format(machine))
    sys.stdout.flush()
    t = Thread(target=_restartVm, args=(machine,))
    t.start()
    while t.is_alive():
        t0 = time.time()
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(max(0, 1 - (time.time() - t0)))
    print('done.')

def createVm(machine):
    if machine in machineList():
        if not isRunning(machine):
            startVm(machine)
    else:
        sys.stdout.write('Creating machine {}'.format(machine))
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

def vagrantList():
    machines = []
    for line in open(os.path.join(DEPLOYMENT_DIR, 'Vagrantfile'), 'r'):
        if 'config.vm.define' in line:
            machines.append(line.split()[1].strip('"'))
    return machines

def machineList(inventory='development'):
    machines = []
    if inventory == 'development':
        cmd = subprocess.Popen(
            'VBoxManage list vms'.split(),
            stdout=subprocess.PIPE
        )
        for line in cmd.stdout:
            line = line.decode()
            if 'discos_' in line:
                m_name = line.split()[0].strip('"').replace('discos_', '')
                machines.append(m_name)
    else:
        h, _, _ = parseInventory(inventory)
        machines = h.keys()
    return machines

def isRunning(name, inventory='development'):
    if name not in machineList():
        error('Machine {} unknown!'.format(name))
    return ping(getIp(name, inventory))

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
            stdout=DEVNULL,
            stderr=DEVNULL
        )
        subprocess.call(
            ['ssh-keyscan', '-H', ip],
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
