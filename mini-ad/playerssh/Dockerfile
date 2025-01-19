# syntax=docker/dockerfile:1
# check=skip=SecretsUsedInArgOrEnv
FROM debian:bookworm

ENV ALLOWED_IPS="AllowUsers player" \
    DEBUG_MODE="false" \
    DEBIAN_FRONTEND=noninteractive \
    # LANG="en_US.UTF-8" \
    # LANGUAGE="en_US.UTF-8" \
    # LC_ALL="en_US.UTF-8" \
    PGID=1000 \
    PUID=1000 \
    SSH_HOST_KEY_DIR="/etc/ssh/ssh_host_keys" \
    SSH_PORT="2222" \
    SSH_USER="player"

ARG PACKAGE_DEPENDENCIES="openssh-server,iputils-ping,wget,curl,locales,tini,tasksel,sudo,vim,nano,tmux"

COPY --chown=root:root --chmod=755 rootfs /

RUN serversideup-dep-install-debian ${PACKAGE_DEPENDENCIES} && \
    tasksel install ssh-server && \
    \
    # Generate required locales
    # echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    # locale-gen && \
    # update-locale LANG=en_US.UTF-8 && \
    \
    # Create user
    serversideup-create-unprivileged-user "$SSH_USER" "${PUID}" "${PGID}" && \
    usermod -a -G sudo "$SSH_USER" &&\
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    \
    # Set proper permissions
    mkdir -p /home/$SSH_USER/.ssh $SSH_HOST_KEY_DIR && \
    chown -R $SSH_USER:$SSH_USER $SSH_HOST_KEY_DIR /home/$SSH_USER/.ssh && \
    chmod 700 /home/$SSH_USER/.ssh && \
    \
    # Create run directory
    mkdir -p /run/sshd && \
    \
    # Remove default SSH host keys
    rm -f /etc/ssh/ssh_host_*_key*

# Expose the SSH port
EXPOSE 2222

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D", "-e"]