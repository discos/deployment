.. _dependencies:

************
Dependencies
************

To automatically deploy DISCOS, you need to install some dependencies:
`Git <https://git-scm.com/>`_, `Ansible <https://www.ansible.com/>`_,
`Python 2.7 <https://www.python.org/download/releases/2.7/>`_,
`Vagrant <https://www.vagrantup.com/>`_ and `VirtualBox
<https://www.virtualbox.org/>`_.  It usually takes about 15 minutes.


Install Git
===========
Before installing Git, verify if it is already installed:

.. code-block:: shell

   $ git --version
   git version 2.17.1

You do not need a particular version of Git, but if the command ``git --version``
fails, than you have to install Git by following the instructions at the `official Git
website <https://git-scm.com/book/en/v1/Getting-Started-Installing-Git>`_.


Install a Python 2.7 environment
================================
The whole DISCOS deployment procedure relies on Python 2.7. Verify if Python 2.7 is already
installed on your system:

.. code-block:: shell

   $ python --version
   Python 2.7.15rc1

If your system comes bundled with a different Python version, you may want to
consider installing a Python 2.7 environment such as
`Anaconda <https://www.anaconda.com/download/#linux>`_,
`Miniconda <https://conda.io/miniconda.html>`_ or
`Pyenv <https://github.com/pyenv/pyenv>`_ and its
`Virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_ plugin.


Install VirtualBox and Vagrant
==============================
You need to install VirtualBox and Vagrant only if you want to
deploy DISCOS on virtual machines, as in the case of a development
environment. As a first step, check if VirtualBox is already installed:

.. code-block:: shell

   $ which virtualbox 
   /usr/bin/virtualbox

In case it is not, download the binary file from the
`official website <https://www.virtualbox.org/wiki/Downloads>`_
and install it.


.. note:: The suggested VirtualBox version to install is the 5.1. As of today,
   the latest release of VirtualBox, version 5.2, seems to introduce some lag
   in SSH sessions to the deployed virtual machines. Version 5.1 also matches
   the VirtualBox guest additions already installed in the virtual machines.


Now verify if Vagrant is installed:

.. code-block:: shell

   $ vagrant --version
   Vagrant 2.2.1

If it is not, download the binary file from
the `vagrant official website <https://www.vagrantup.com/downloads.html>`_
and install it.


At this point you are ready to deploy DISCOS.  The :ref:`deploy_quickstart`
section is a good starting point, because it covers a typical scenario.
