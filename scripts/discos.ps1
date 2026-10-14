#Requires -Version 7.3
<#
.SYNOPSIS
    PowerShell wrappers for the DISCOS deployment tools installed in WSL2.

.DESCRIPTION
    Ansible cannot run on Windows, so discos-deploy and the other tools run
    inside a WSL2 distribution. These functions forward each call to that
    distribution, passing the arguments through unchanged.

    Requirements inside the distribution:
      - the deployment package installed, so the tools are on the login
        PATH (~/.local/bin);
      - the Docker engine installed in the distribution itself, not Docker
        Desktop: with Docker Desktop the container IPs (192.168.56.0/24)
        are not reachable from WSL;
      - REPOSITORY_TOKEN exported in ~/.profile, since a non-interactive
        login shell does not read ~/.bashrc.

    File arguments must be WSL paths (/mnt/d/... or ~/...), not Windows ones.

.EXAMPLE
    . D:\Work\Develop\deployment\scripts\discos.ps1
    discos-deploy manager:development --docker
    discos-container status
    discos-login manager

    Add the first line to $PROFILE to load the functions in every session.
    Set $env:DISCOS_WSL_DISTRO to use a distribution other than 'Ubuntu-26.04'.
#>

$DiscosWslDistro = if ($env:DISCOS_WSL_DISTRO) { $env:DISCOS_WSL_DISTRO } else { 'Ubuntu-26.04' }

# A login shell loads PATH and REPOSITORY_TOKEN from ~/.profile;
# "$0" "$@" hands the arguments over without re-parsing them.
$DiscosWslPrefix = @(
    '-d', $DiscosWslDistro, '--cd', '~', '--exec',
    'bash', '-lc', 'exec "$0" "$@"'
)

function discos-deploy    { wsl.exe @DiscosWslPrefix discos-deploy @args }
function discos-container { wsl.exe @DiscosWslPrefix discos-container @args }
function discos-login     { wsl.exe @DiscosWslPrefix discos-login @args }
