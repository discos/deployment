#! /usr/bin/env bash

if [ -f $HOME/bin/_discos-check-branch ]; then
	CHECK_OUTPUT=$($HOME/bin/_discos-check-branch)
	if [ -n "${CHECK_OUTPUT}" ]; then
		echo -e "${pur}WARNING:${txtrst} $CHECK_OUTPUT"
	fi
fi

# Load DISCOS environment
# =======================
if [ -f /{{ discos_sw_dir }}/config/misc/load_branch ]; then
    source /{{ discos_sw_dir }}/config/misc/load_branch
fi

# Set the STATION
# ===============
if [ -f /{{ discos_sw_dir }}/config/misc/station ]; then
    source /{{ discos_sw_dir }}/config/misc/station
elif [ -n "${DISCOS_BRANCH}" ]; then
    if [ -f $INTROOT/.station ]; then
        source $INTROOT/.station
    fi
else
    unset STATION
fi

export ACS_TMP=/service/acstmp/{{ inventory_hostname_short }}

# Load ACS definitions
# ====================
if [ -f /{{ discos_sw_dir }}/config/acs/.bash_profile.acs ]; then
    source /{{ discos_sw_dir }}/config/acs/.bash_profile.acs
fi

# Set the CDB
# ===========
if [ -n "${DISCOS_BRANCH}" ]; then
    if [ $CDB = "test" ]; then
        export ACS_CDB=/{{ discos_sw_dir }}/{{ user.name }}/$DISCOS_BRANCH/$STATION
    else
        export ACS_CDB=/{{ discos_sw_dir }}/{{ user.name }}/$DISCOS_BRANCH/$STATION/Configuration
    fi
fi

# Set the prompt
# ==============
if [ -n "${DISCOS_BRANCH}" ]; then
    PS1="(\[$grn\]$DISCOS_BRANCH\[$txtrst\]:\[$cyn\]$CDB\[$txtrst\]) \u@\h \w $ "
else
    PS1="(\[$red\]branch?\[$txtrst\]) \u@\h \w $ "
fi

# Remove duplicates from PATH environment variables
# =================================================

for oldvariable in `env | grep "PATH" | grep -v "PATH_SEP" | awk -F= '{print $1}'`; do
    newvariable=
    oldifs=$IFS
    IFS=":"
    declare -A exists
    for entry in ${!oldvariable}; do
        if [ ! -z "$entry" ] && [ -z ${exists[$entry]} ]; then
            newvariable=${newvariable:+$newvariable:}$entry
            exists[$entry]=yes
        fi
    done
    unset exists
    IFS=$oldifs
    unset oldifs
    export $oldvariable="$newvariable"
    unset newvariable
done
