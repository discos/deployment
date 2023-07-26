import os
import unittest
from subprocess import Popen, PIPE

BASECMD = ['discos-deploy', '--sim']


class TestDeployCLI(unittest.TestCase):

    def test_cannot_split_the_system_in_cluster_and_env(self):
        """Cluster and env are not separated by :"""
        cmd = BASECMD + ['discos_development']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(err, b'You must specify an available system.')

    def test_too_much_separators(self):
        """Too much : separators"""
        cmd = BASECMD + ['large:development:srt']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(err, b'You must specify an available system.')

    def test_wrong_cluster_and_right_env(self):
        """The user specify a wrong_cluster and right_env"""
        cmd = BASECMD + ['wrong_cluster:development']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(err, b'"wrong_cluster" not found')

    def test_right_cluster_and_wrong_env(self):
        """The user specify a right_cluster and wrong_env"""
        cmd = BASECMD + ['large:wrong_env']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(err, b'System "large:wrong_env" not recognized')

    def test_wrong_cluster_and_wrong_env(self):
        """The user specify a wrong_cluster and wrong_env"""
        cmd = BASECMD + ['wrong:wrong']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(err, b'System "wrong:wrong" not recognized')

    def test_no_deploy(self):
        """Do not set branch to deploy"""
        cmd = BASECMD + ['acs:development']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertNotRegex(out, b'branch=')
        self.assertNotRegex(out, b'cdb=')
        self.assertNotRegex(out, b'station=')

    def test_deploy_branch(self):
        """Set a branch and a station"""
        cmd = BASECMD + [
            'acs:development',
            '--branch',
            'stable',
            '--station',
            'srt'
        ]
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(
            out,
            b'--extra-vars cdb=test station=SRT branch=stable'
        )

    def test_deploy_branch_no_station(self):
        """Set the arg '--branch' but not the station"""
        cmd = BASECMD + ['acs:development', '--branch', 'stable']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(
            err,
            b"'--station' argument must be specified."
        )

    def test_deploy_wrong_station(self):
        """Deploy onto SRT with '--station=medicina'"""
        cmd = BASECMD + [
            'acs:srt',
            '--branch',
            'stable',
            '--station',
            'medicina'
        ]
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(
            err,
            b'you cannot specify a different station.'
        )

    def test_bring_machines_up(self):
        """Test if machines are brought up"""
        cmd = BASECMD + ['discos:development']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegex(out, b'Starting machine manager....done.')

    def test_bring_single_machine_up(self):
        """Test if machine manager is brought up"""
        cmd = BASECMD + ['manager:development']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertNotRegex(out, b'Starting machine storage....done.')
        self.assertRegex(out, b'Starting machine manager....done.')
        self.assertNotRegex(out, b'Starting machine console....done.')

    def test_do_not_use_vagrant(self):
        """Do not use vagrant in development environment"""
        cmd = BASECMD + ['discos:development', '--no-vagrant']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertNotRegex(out, b'Starting machine storage....done.')
        self.assertNotRegex(out, b'Starting machine manager....done.')
        self.assertNotRegex(out, b'Starting machine console....done.')


if __name__ == '__main__':
    unittest.main()
