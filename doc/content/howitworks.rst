.. _howitworks:

************
How it works
************

The `DISCOS Deployment` tool basically acts as a `wrapper` of a very powerful
automation tool called `Ansible <https://www.ansible.com/>`_, described below.

=======
Ansible
=======

Ansible is a very well known software among IT professionals, since it offers
wide cross-platform provisioning capabilities. It works by applying a series of
pre-defined and ordered tasks to a target machine over an SSH connection. By
customizing the tasks and their order, it is possible to apply a complex
configuration to the designated target machine, taking care of every library,
dependency or package that has to be installed, of every user that has to be
added or removed, of every configuration file that has to be taken care of,
and applying a vast plethora of other tasks that will result in a custom
configuration of the target machine.
Another huge advantage of using Ansible, is that by relying on an SSH
connection to run its tasks, they can be run in parallel on multiple machines.
This becomes especially useful when you have to apply the same configuration
(or part of it) on several machines. Each task can be parametrized, this means
that it will be executed in the same manner on each target machine, but it will
use a specific parameter for each target machine (I.e.: a task that uses the IP
address of the target machine will use the correct address for each machine it
will run onto).
Pretty much all the files used by Ansible to perform its tasks are written in
`YAML <https://en.wikipedia.org/wiki/YAML/>`_, along with the files in which
parameters are stored.
When referring to Ansible components, a collection of parameters is called
`inventory`, a collection of tasks is called `role`, whether a collection of
roles is called `playbook`. In order to build project that uses Ansible
correctly, the following directory structure has to be followed:

::

   ansible
   ├── ansible.cfg
   ├── playbook_1.yml
   ├── playbook_2.yml
   ├── group_vars
   │   ├── group_1.yml
   │   └── group_2.yml
   ├── inventories
   │   ├── inventory_1
   │   │   ├── group_vars
   │   │   │   ├── all.yml
   │   │   │   └── group_1.yml
   │   │   └── hosts.yml
   │   └── inventory_2
   │       ├── group_vars
   │       │   ├── all.yml
   │       │   └── group_2.yml
   │       └── hosts.yml
   └── roles
       ├── role_1
       ├── role_2
       ├── role_3
       └── role_4


-----------
Inventories
-----------

---------
Playbooks
---------

-----
Roles
-----






============
Dependencies
============

One of the main tasks of the provisioning process is to install some
dependencies needed for the DISCOS software to operate correctly
The very first role Ansible executes takes care of downloading the necessary
files 
