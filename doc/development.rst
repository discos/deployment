.. _deploy_development:

***********
Development
***********

This section describes how to deploy a DISCOS development environment.

The development environment currently consists of a single machine:

- ``manager``

Even though the deployment system supports multiple machines and clusters,
the development setup is intentionally minimal.

Command syntax
==============

::

   discos-deploy <target>:<environment> [options]

In development environments, the ``--station`` option is required when
deploying DISCOS software.

Deploy the development machine
==============================

To deploy the development environment:

Docker-based deployment (recommended)
-------------------------------------

::

   $ discos-deploy manager:development --docker

This will:

- create a Docker container
- configure networking
- inject SSH keys
- apply the full Ansible configuration


Virtual machine deployment
--------------------------

::

   $ discos-deploy manager:development

This will create and provision a virtual machine using Vagrant.


Existing machines
-----------------

If the target machine already exists (physical or virtual), you can deploy
directly onto it:

::

   $ discos-deploy manager:development --no-vagrant

The machine must be reachable via SSH.


Notes on clusters
=================

The deployment system supports clusters of machines through Ansible inventories.

In the development environment, however, only the ``manager`` machine is defined.

For multi-machine deployments, refer to :ref:`deploy_production`.


What happens during deployment
==============================

The deployment procedure:

- connects to the target machine via SSH
- configures users and permissions
- installs system dependencies
- configures networking and services
- installs ACS and DISCOS dependencies

The process is idempotent: running it multiple times produces the same result.


DISCOS setup
============

Manual setup
------------

To download the DISCOS control software:

::

   $ discos-get master --station SRT

Then build and install:

::

   $ make
   $ make install


Automatic setup
---------------

The deployment procedure can also install DISCOS automatically:

::

   $ discos-deploy manager:development --branch discos1.0-rc02 --station Noto

This will:

- download the specified branch or tag
- configure the environment
- prepare the system for building

The ``--station`` argument is required in development environments, since
machines are generic and not tied to a specific station.


Notes
=====

- Docker is the recommended approach for development environments
- Virtual machines are supported for compatibility
- Physical machines can always be used if already available
