.. _deploy_quickstart:

***********
Quick start
***********

If you have installed the dependencies described in section
:ref:`dependencies`, you are ready to deploy a DISCOS environment.

Clone the repository
====================

Download the DISCOS deployment repository:

.. code-block:: shell

   $ git clone git@github.com:discos/deployment.git
   $ cd deployment

.. note::

   Authentication to GitHub requires a valid
   `SSH key <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/>`_.


Install the package
===================

Install Python dependencies:

.. code-block:: shell

   $ pip install -r requirements.txt

Install the deployment package:

.. code-block:: shell

   $ python setup.py install

Alternatively:

.. code-block:: shell

   $ python setup.py install --user
   $ source ~/.bashrc


Deployment model
================

The deployment procedure is handled by the :file:`discos-deploy` script.

It uses Ansible to configure a set of target machines. These machines can be:

- physical machines
- virtual machines
- Docker containers

The same procedure is applied in all cases.

Command syntax
==============

The ``discos-deploy`` command has the following form:

::

   discos-deploy <target>:<environment> [options]

Where:

- ``<target>`` is a machine or a cluster
- ``<environment>`` identifies the Ansible inventory

Common options include:

- ``--docker``: use Docker containers
- ``--no-vagrant``: deploy on existing machines
- ``--branch`` / ``--tag``: select DISCOS version
- ``--station``: required in development environments

Provision a development environment
===================================

Docker-based deployment (recommended)
-------------------------------------

The recommended way to deploy a development environment is using Docker:

.. code-block:: shell

   $ discos-deploy manager:development --docker

This command will:

- create a Docker container
- configure networking
- inject SSH keys
- apply the full Ansible configuration

This approach provides fast and reproducible environments and is suitable
for development and testing.


Virtual machine deployment
--------------------------

You can also deploy the environment using virtual machines:

.. code-block:: shell

   $ discos-deploy manager:development

This will create and provision a virtual machine using Vagrant and VirtualBox.

.. note::

   Virtual machines are kept for compatibility, but Docker is the recommended
   approach for development.


Physical machines
-----------------

If you already have a set of machines available, you can deploy DISCOS
directly on them:

.. code-block:: shell

   $ discos-deploy manager:development --no-vagrant

In this case, the machines must be reachable via SSH.


Understanding the command
=========================

The argument:

::

   manager:development

means:

- ``manager`` → target machine or cluster
- ``development`` → environment (Ansible inventory)

The deployment process is idempotent: running the command multiple times
will not change the final result, and subsequent runs are usually faster.


Access the system
=================

Once the deployment is complete, access the machine via SSH:

.. code-block:: shell

   $ ssh discos@<manager IP address>

Alternatively, you can use the :file:`discos-login` script described in
:ref:`deploy_scripts`.

.. _get_a_discos_branch:

Get a DISCOS branch
===================

After login, no DISCOS branch is active yet:

.. code-block:: shell

   (branch?) discos@manager ~ $

To download and activate a branch:

.. code-block:: shell

   $ discos-get master --station SRT

The environment will be configured accordingly.

.. _install_discos:

Install DISCOS
==============

To build and install DISCOS:

.. code-block:: shell

   $ make
   $ make install

.. note::

   The build process may take a long time depending on the system.


Next steps
==========

This quick start covers a minimal development setup.

For more advanced scenarios:

- multiple machines → see :ref:`deploy_development`
- production systems → see :ref:`deploy_production`
