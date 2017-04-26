.. _deploy_production:

**********
Production
**********

To deploy the system in production, just execute the ``build`` script twice:

.. code-block:: shell

  $ ./build large:production
  $ ./build large:production --deploy srt-0.1

.. note:: According to the `Automatic deployment task
   <https://trello.com/c/D7NfvQOV>`_, in the future you can do it by using
   only one command: ``./build large:production --provision --deploy srt-0.1``.

The first command, ``./build large:production``, provisions a *large* system,
composted of three machines (``manager``, ``as`` and ``ms``).  The second
command uses the ``--deploy`` switch in order to deploy the ``srt-0.1`` branch.

If you only want to provision or deploy one single machine, change ``large`` to
the related machine name.  For instance, in the following case we are deploying
the only ``ms`` (minor servo) machine:

.. code-block:: shell

  $ ./build ms:production
  $ ./build ms:production --deploy srt-0.1
