.. _deploy_production:

**********
Production
**********

This section describes how to deploy DISCOS in a production environment.

The deployment procedure configures target machines via SSH using Ansible.


Command syntax
==============

The deployment is performed using the ``discos-deploy`` command:

::

   discos-deploy SYSTEM [options]

where ``SYSTEM`` has the form:

::

   <target>:<environment>

``<target>`` can be either a machine name or a cluster name, while
``<environment>`` identifies the target inventory.


Deploy the full system
======================

To deploy the full production system for a station:

::

   $ discos-deploy discos:SRT

The ``discos`` target identifies the full cluster of machines defined in the
selected production inventory.

This command connects to all target machines via SSH and applies the full
configuration.


Deploy a single machine
=======================

To deploy a single production machine:

::

   $ discos-deploy console:SRT

This command applies the configuration only to the selected machine.


Command line options
====================

The most relevant options for production deployments are:

``-b``, ``--branch BRANCH``
   Deploy the specified DISCOS branch or tag.

``-s``, ``--station STATION``
   Specify the station name.

``--deploy-only``
   Only deploy the DISCOS Control Software.

``--test-cdb-only``
   Only test the DISCOS CDB.

``--default-passwords``
   Use the default passwords for the DISCOS users.

``--sim``
   Print the final Ansible command without executing it.

``-v``, ``--verbose``
   Run Ansible in verbose mode.


Options behavior
================

In production environments, the station name is implicitly derived from the
selected environment. For example:

::

   $ discos-deploy discos:SRT

already implies station ``SRT``.

For this reason, the ``--station`` option is normally not required in
production. If specified, it must match the environment name.

When using ``--branch``, the station must be defined. In production this
usually happens automatically through the selected environment.

The ``--deploy-only`` and ``--test-cdb-only`` options are mutually exclusive.

The ``--deploy-only`` option requires ``--branch``.


DISCOS setup
============

Manual setup
------------

To install the DISCOS control software manually, use the ``discos-get`` command
and then build and install the system as described in
:ref:`get_a_discos_branch` and :ref:`install_discos`.

In production environments, it is usually preferable to work on a specific tag.


Automatic setup
---------------

The deployment procedure can also install DISCOS automatically:

::

   $ discos-deploy discos:SRT --branch stable

or:

::

   $ discos-deploy discos:SRT --branch discos1.0-rc02

In both cases the deployment procedure will pass the required variables to
Ansible and execute the corresponding deployment tasks.


Execution model
===============

The deployment procedure:

- connects to target machines via SSH
- applies the Ansible configuration for the selected environment
- installs system dependencies and DISCOS components
- configures the runtime environment

All target machines must already be reachable through the network and properly
configured for SSH access.
