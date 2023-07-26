#!/usr/bin/env python
import os
import shutil

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

scripts = ['discos-deploy', 'discos-vms', 'discos-vnc', 'discos-login']
scripts = [os.path.join('scripts', s) for s in scripts]

setup(
    name='discos-deployment',
    version='1.0',
    description='Ansible-automated setup procedure of DISCOS machines.',
    author='Marco Buttu, Giuseppe Carboni',
    author_email='marco.buttu@inaf.it',
    maintainer='Giuseppe Carboni',
    maintainer_email='giuseppe.carboni@inaf.it',
    url='https://github.com/discos/deployment/',
    packages=['deployment'],
    scripts=scripts,
    platforms='all',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10.7',
    ]
)

deployment_env = os.path.join(os.environ['HOME'], '.deployment')
vagrantfile_dst = os.path.join(deployment_env, 'Vagrantfile')
ansible_dst = os.path.join(deployment_env, 'ansible')

if not os.path.exists(deployment_env):
    os.mkdir(deployment_env)
if os.path.exists(ansible_dst):
    shutil.rmtree(ansible_dst)

shutil.copyfile('Vagrantfile', vagrantfile_dst)
shutil.copytree('ansible', ansible_dst)
