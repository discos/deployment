FROM centos:7.9.2009

ENV HOSTNAME=discos-manager

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

RUN yum install -y dbus dbus-x11 openssh-server python3 && yum clean all

RUN rm -f /etc/machine-id /var/lib/dbus/machine-id && \
    dbus-uuidgen --ensure=/etc/machine-id && \
    ln -sf /etc/machine-id /var/lib/dbus/machine-id

RUN ssh-keygen -A
RUN echo 'root:rootpwd' | chpasswd

COPY third-party/docker-systemctl-replacement/systemctl3.py /usr/local/bin/systemctl
COPY third-party/docker-systemctl-replacement/journalctl3.py /usr/local/bin/journalctl
RUN chmod +x /usr/local/bin/systemctl /usr/local/bin/journalctl

RUN /usr/local/bin/systemctl enable sshd

CMD ["/usr/bin/python3", "/usr/local/bin/systemctl", "init"]
