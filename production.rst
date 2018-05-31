.. _deploy_production:

**********
Production
**********

To deploy the system in production, you have to specify a *cluster* of machines,
and the name of the station:

.. code-block:: shell

  $ discos-deploy discos:srt

As seen in the :ref:`deploy_development`, you can choose a station
among ``medicina``, ``noto``, ``srt``.
To deploy the ``discos`` control software, you can optionally pass
the ``--deploy`` argument followed by the desired branch:

.. code-block:: shell

  $ discos-deploy discos:srt --deploy latest64

In this case, where the station is already specified,
you can omit the ``--station`` argument. If you decide to specify the
``--station`` argument anyway, if the given argument does not match the
correct station you will receive an error.
The first command, ``discos-deploy discos:srt``, provisions the complete *discos* system,
composed of all the selected station machines
(in case of ``srt`` station, ``manager``, ``as`` and ``ms``).
The second command also uses the ``--deploy`` argument
in order to deploy the ``latest64`` branch.

If you only want to provision or deploy one single machine, change the cluster
from ``discos`` to the related machine name. For instance, in the following
case we are deploying only the ``ms`` (minor servo) machine:

.. code-block:: shell

  $ discos-deploy ms:srt
  $ discos-deploy ms:srt --deploy latest64
