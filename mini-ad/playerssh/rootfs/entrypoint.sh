#!/bin/sh
set -e
default_uid='1000'
default_gid='1000'
default_unprivileged_user='player'
ssh_user=${SSH_USER:-"${default_unprivileged_user}"}
ssh_host_key_dir=${SSH_HOST_KEY_DIR:-"/etc/ssh/ssh_host_keys"}
ssh_user_home="/home/${ssh_user}"
ssh_port=${SSH_PORT:-"2222"}


if [ "$DEBUG" = "true" ]; then
    set -x
fi

######################################################
# Functions
######################################################
debug_print() {
    if [ "$DEBUG" = "true" ]; then
        echo "$1"
    fi
}

validate_allowed_ips() {
    local ips="$1"
    # Validate AllowUsers entries and IP addresses
    if ! echo "$ips" | grep -E '^(AllowUsers|from) [a-zA-Z0-9@., ]+$'; then
        echo "Invalid ALLOWED_IPS format"
        exit 1
    fi
}

######################################################
# Main
######################################################
# Rename the Ansible user if it doesn't match the default
if [ "$ssh_user" != "$default_unprivileged_user" ]; then

    debug_print "Renaming user \"$default_unprivileged_user\" to \"$ssh_user\"..."

    # Check if we're on Alpine or Debian
    if [ -f /etc/alpine-release ] || [ -f /etc/debian_version ]; then
        # Rename user and group
        usermod -l "$ssh_user" "$default_unprivileged_user" || { echo "Failed to rename user"; exit 1; }
        groupmod -n "$ssh_user" "$default_unprivileged_user" || { echo "Failed to rename group"; exit 1; }
        
        # Update home directory and move contents to new home directory
        usermod -d "/home/$ssh_user" -m "$ssh_user" || { echo "Failed to update home directory"; exit 1; }
        
        if [ -f /etc/debian_version ]; then
            # Update default group for Debian-based systems
            usermod -g "$ssh_user" "$ssh_user" || { echo "Failed to update default group"; exit 1; }
        fi
        
        debug_print "User and group renamed successfully. Home directory updated."
    else
        echo "Unsupported distribution for renaming user."
        exit 1
    fi
fi

# Change the SSH user and group to the specified UID and GID if they are not the default
if { [ ! -z "${PUID}" ] && [ "${PUID}" != "$default_uid" ]; } || { [ ! -z "${PGID}" ] && [ "${PGID}" != "$default_gid" ]; }; then
    debug_print "Preparing environment for $PUID:$PGID..."
    
    # Handle existing user with the same UID
    if id -u "${PUID}" >/dev/null 2>&1; then
        old_user=$(id -nu "${PUID}")
        debug_print "UID ${PUID} already exists for user ${old_user}. Moving to a new UID."
        usermod -u "999${PUID}" "${old_user}"
    fi

    # Handle existing group with the same GID
    if getent group "${PGID}" >/dev/null 2>&1; then
        old_group=$(getent group "${PGID}" | cut -d: -f1)
        debug_print "GID ${PGID} already exists for group ${old_group}. Moving to a new GID."
        groupmod -g "999${PGID}" "${old_group}"
    fi

    # Change UID and GID of ssh_user user and group
    usermod -u "${PUID}" "${ssh_user}" 2>&1 >/dev/null || echo "Error changing user ID."
    groupmod -g "${PGID}" "${ssh_user}" 2>&1 >/dev/null || echo "Error changing group ID."

fi

# Set SSHD configuration
echo "🤖 Setting SSHD configuration..."
{
    echo "Port ${ssh_port}"
    echo "PermitRootLogin no"
    echo "DebianBanner no"
    echo "PermitEmptyPasswords no"
    echo "MaxAuthTries 5"
    echo "LoginGraceTime 20"
    echo "ChallengeResponseAuthentication no"
    echo "KerberosAuthentication no"
    echo "GSSAPIAuthentication no"
    echo "X11Forwarding no"
    echo "AllowAgentForwarding yes"
    echo "AllowTcpForwarding yes"
    echo "PermitTunnel yes"
    echo "HostKey ${ssh_host_key_dir}/ssh_host_rsa_key"
    echo "HostKey ${ssh_host_key_dir}/ssh_host_ecdsa_key"
    echo "HostKey ${ssh_host_key_dir}/ssh_host_ed25519_key"
    echo "SyslogFacility AUTH"
    echo "LogLevel VERBOSE"
    # Enable MOTD display
    echo "PrintMotd yes"
    echo "PrintLastLog yes"
    # Strict authentication
    echo "PasswordAuthentication no"
    echo "UsePAM no"
    echo "AuthenticationMethods publickey"
    # Brute force protection
    echo "MaxSessions 10"
    echo "MaxAuthTries 3"
    echo "LoginGraceTime 15"
    echo "MaxStartups 10:30:100"
    echo "ClientAliveInterval 300"
    echo "ClientAliveCountMax 2"
} > /etc/ssh/sshd_config.d/custom.conf

if [ "$DEBUG" = "true" ]; then
    echo "🔥🔥🔥 Putting SSH server into Debug Mode..."
    {
        echo "SyslogFacility AUTHPRIV"
        echo "LogLevel DEBUG"
    } >> /etc/ssh/sshd_config.d/custom.conf
fi

# Check if SSH host keys are missing
if [ ! -f "${ssh_host_key_dir}/ssh_host_rsa_key" ] || [ ! -f "${ssh_host_key_dir}/ssh_host_ecdsa_key" ] || [ ! -f "${ssh_host_key_dir}/ssh_host_ed25519_key" ]; then
    echo "🏃‍♂️ Generating SSH keys for you..."
    
    # Create host key directory if it doesn't exist
    mkdir -p "${ssh_host_key_dir}"
    
    # Generate the host keys directly
    ssh-keygen -q -N "" -t rsa -f "${ssh_host_key_dir}/ssh_host_rsa_key"
    ssh-keygen -q -N "" -t ecdsa -f "${ssh_host_key_dir}/ssh_host_ecdsa_key"
    ssh-keygen -q -N "" -t ed25519 -f "${ssh_host_key_dir}/ssh_host_ed25519_key"
    
    # Set proper permissions
    chmod 600 "${ssh_host_key_dir}"/ssh_host_*_key
    chmod 644 "${ssh_host_key_dir}"/ssh_host_*_key.pub
fi

# Configure allowed IPs
validate_allowed_ips "${ALLOWED_IPS}"
if [ -z "${ALLOWED_IPS}" ]; then
    echo "🚨🚨🚨 CONFIGURATION ERROR:"
    echo "ALLOWED_IPS environment variable is not set."
    exit 1
else
    echo "📡 Setting allowed IPs (from ALLOWED_IPS variable) ..."
    echo "${ALLOWED_IPS}" >> /etc/ssh/sshd_config.d/custom.conf
fi

# Setup authorized keys
mkdir -p "${ssh_user_home}/.ssh/"

if [ -n "$AUTHORIZED_KEYS" ] && [ ! -f "${ssh_user_home}/.ssh/authorized_keys" ]; then
    echo "🔑 Setting authorized keys (from AUTHORIZED_KEYS variable)..."
    echo "${AUTHORIZED_KEYS}" > "${ssh_user_home}/.ssh/authorized_keys"
elif [ -z "$AUTHORIZED_KEYS" ] && [ -f /authorized_keys ]; then
    echo "🔐 Using the provided authorized_keys file..."
    cp /authorized_keys "${ssh_user_home}/.ssh/authorized_keys"
elif [ -n "$AUTHORIZED_KEYS" ] && [ -f /authorized_keys ]; then
    echo "⚠️ WARNING: Both AUTHORIZED_KEYS and authorized_keys file are set."
    echo "ℹ️ INFO: We'll be using the AUTHORIZED_KEYS variable to configure SSH."
    echo "${AUTHORIZED_KEYS}" > "${ssh_user_home}/.ssh/authorized_keys"
else
    echo "🚨🚨🚨 CONFIGURATION ERROR:"
    echo "You must either set the AUTHORIZED_KEYS"
    echo "environment variable or mount a configuration file to"
    echo "${ssh_user_home}/.ssh/authorized_keys."
    exit 1
fi

# Set proper permissions
debug_print "Changing ownership of all files and directories..."
chown "${PUID}:${PGID}" \
    "${ssh_user_home}" \
    "${ssh_host_key_dir}" \
    "${ssh_user_home}/.ssh" \
    "${ssh_user_home}/.ssh/authorized_keys"
chmod 700 \
    "${ssh_user_home}/.ssh" \
    "${ssh_user_home}/.ssh/authorized_keys"
# Ensure strict permissions on SSH configuration
chmod 600 /etc/ssh/sshd_config.d/*.conf
chmod 755 /etc/ssh/sshd_config.d

# Create a custom MOTD

{
    echo '\033[38;5;75m╭──────────────────────────────────────────────────────╮\033[0m'
    echo '\033[38;5;75m│                      🔐 Mini-AD                      |\033[0m'
    echo '\033[38;5;75m╰──────────────────────────────────────────────────────╯\033[0m'
    echo '---------------------------------------------------------'
    echo ' Infra Docker Diagram '
    echo '                                                         '
    echo '                                         Attacker        '
    echo '                                            │            '
    echo '                                    Internet│80/tcp      '
    echo '                                            │            '
    echo '                  ....................┌─────▼─────┐......'
    echo '                  :Docker netowrk     │           │      '
    echo '                  :                   │   proxy   │      '
    echo '                  :                   │ 10.0.1.10 │      '
    echo '                  :                   └─────┬─────┘      '
    echo '                  :                         │            '
    echo '                  :                         │80/tcp      '
    echo '                  :                         │            '
    echo '                  ┌───────────┐       ┌─────▼─────┐      '
    echo '         2222/tcp │           │       │           │      '
    echo 'Defender ────────►│    ssh    │       │    web    │      '
    echo '         Internet │ 10.0.1.30 │       │ 10.0.1.20 │      '
    echo '                  └─────┬─────┘       └─────▲─────┘      '
    echo '                  :     │                   │            '
    echo '                  :     │ Volume monuts     │            '
    echo '                  :     └───────────────────┘            '
    echo '                  :     /var_www_html:/var/www/html      '
    echo '                  :     /var_log_apache2:/var/log/apache2'
    echo '                  :                                      '
    echo '---------------------------------------------------------'
    echo ''
} > /etc/motd

# Execute the CMD
exec "$@"