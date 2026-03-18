.. _dependencies:

************
Dependencies
************

This section describes the required dependencies to deploy DISCOS.

The deployment procedure is based on Ansible and is designed to configure
a set of target machines. These machines can be:

- physical machines
- virtual machines
- Docker containers

The same procedure is applied in all cases.

Mandatory dependencies
======================

The following tools are always required:

- `Git <https://git-scm.com/>`_
- `Python 3 <https://www.python.org/download/>`_
- `Ansible <https://www.ansible.com/>`_

Install Git
-----------

Before installing Git, verify if it is already available:

.. code-block:: shell

   $ git --version

If the command fails, install Git following the instructions at the
`official Git website <https://git-scm.com/book/en/v1/Getting-Started-Installing-Git>`_.

Install Python 3
----------------

Verify that Python 3 is installed:

.. code-block:: shell

   $ python --version

If your system provides an older version of Python, consider installing a
dedicated Python environment such as:

- `Anaconda <https://www.anaconda.com/docs/main>`_
- `Miniconda <https://conda.io/miniconda.html>`_
- `Pyenv <https://github.com/pyenv/pyenv>`_ with
  `Virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_


Install Ansible
---------------

Ansible is the core tool used to configure the target machines.

You can install it using ``pip``:

.. code-block:: shell

   $ pip install ansible

Alternatively, you can install it using your system package manager.


Execution environments
======================

The deployment procedure can be applied to different types of environments.
Depending on the chosen target, additional tools may be required.

Docker containers (recommended for development)
-----------------------------------------------

Docker is the recommended way to create development environments.

It allows you to quickly provision disposable systems that behave like
real machines, while reusing the same Ansible configuration used for
physical deployments.

Install Docker:

.. code-block:: shell

   $ sudo apt install docker.io
   $ sudo usermod -aG docker $USER

After installation, log out and log back in to apply group changes.

Verify the installation:

.. code-block:: shell

   $ docker --version


Virtual machines
----------------

Virtual machines can be used as an alternative to Docker containers,
or when a full system emulation is required.

To use them, install:

- `VirtualBox <https://www.virtualbox.org/>`_
- `Vagrant <https://developer.hashicorp.com/vagrant/>`_

Install VirtualBox:

.. code-block:: shell

   $ which virtualbox

If not installed, download it from the
`VirtualBox official website <https://www.virtualbox.org/wiki/Downloads>`_.

Install Vagrant:

.. code-block:: shell

   $ vagrant --version

If not installed, download it from the
`Vagrant install page <https://developer.hashicorp.com/vagrant/install>`_.


Physical machines
-----------------

No additional software is required to deploy on physical machines.

You only need:

- network connectivity
- SSH access from the control host


Summary
=======

- Git, Python 3 and Ansible are always required
- The deployment procedure targets machines via Ansible
- Docker and virtual machines are optional tools to create such machines
- Physical machines are supported out of the box

Once all dependencies are installed, proceed to the
:ref:`deploy_quickstart` section.
