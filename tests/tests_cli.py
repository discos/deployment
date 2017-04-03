import os
import unittest
from subprocess import Popen, PIPE

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_DIR = TESTS_DIR.rstrip('tests')
SCRIPT = os.path.join(SCRIPT_DIR, 'build')
BASECMD = ['python', SCRIPT, '--sim']


class TestCLI(unittest.TestCase):

    def test_cannot_split_the_system_in_cluster_and_env(self):
        """Cluster and env are not separated by :"""
        cmd = BASECMD + ['discos_srt_development']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(err, b'You must specify an available system.')

    def test_too_much_separators(self):
        """Too much : separators"""
        cmd = BASECMD + ['discos_srt:development:srt']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(err, b'You must specify an available system.')

    def test_wrong_cluster_and_right_env(self):
        """The user specify a wrong_cluster and right_env"""
        cmd = BASECMD + ['wrong_cluster:development']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(err, b'"wrong_cluster" not found')

    def test_right_cluster_and_wrong_env(self):
        """The user specify a right_cluster and wrong_env"""
        cmd = BASECMD + ['discos_srt:wrong_env']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(err, b'"wrong_env" not found')

    def test_wrong_cluster_and_wrong_env(self):
        """The user specify a wrong_cluster and wrong_env"""
        cmd = BASECMD + ['wrong:wrong']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(err, b'System "wrong:wrong" not recognized')

    def test_no_deploy(self):
        """Do not set the tag 'deploy'"""
        cmd = BASECMD + ['discos_noto:development']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertNotRegexpMatches(out, b'branch')
        self.assertNotRegexpMatches(out, b'--tags')

    def test_deploy_branch(self):
        """Set the tag 'deploy'"""
        cmd = BASECMD + ['discos_srt:development', '--deploy', 'srt-0.1']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(out, b'branch=srt-0.1')
        self.assertRegexpMatches(out, b'--tags deploy')

    def test_deploy_master_no_station(self):
        """Require the station in case of master branch"""
        cmd = BASECMD + ['discos_srt:development', '--deploy', 'master']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(err, b'--station is required')

    def test_deploy_master(self):
        """Set the station"""
        cmd = BASECMD + [
            'discos_noto:development',
            '--deploy',
            'master',
            '--station', 'srt']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(out, b'station=srt')

    def test_only_master_accepts_station(self):
        """You can not set the -s if the branch is not master."""
        cmd = BASECMD + [
            'discos_srt:development',
            '--deploy',
            'srt-0.1',
            '--station',
            'medicina']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(err, b'only master branch accepts the -s')

    def test_deploy_github_username(self):
        """Pass the GitHub username from command line"""
        cmd = BASECMD + [
            'discos_noto:development',
            '--deploy',
            'srt-0.1',
            '--user', 'pippo']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(out, b'ghuser=pippo')

    def test_deploy_github_username_requires_deploy(self):
        """Pass the GitHub username from command line"""
        cmd = BASECMD + [
            'discos_noto:development',
            '--user', 'pippo']
        pipes = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = pipes.communicate()
        self.assertRegexpMatches(err, b'--user requires --deploy')


if __name__ == '__main__':
    unittest.main()
