/etc/ssh/sshd_config:
  cmd.run:
    - names:
      - sed -i '/#UsePAM/s/#UsePAM no/UsePAM yes/g' /etc/ssh/sshd_config
    - unless: grep 'UsePAM yes' /etc/ssh/sshd_config

/etc/pam.d/login:
  file.append:
    - text:
      - "session    required    pam_limits.so"

/etc/security/limits.conf:
  file.append:
    - text:
      - "*        -    nofile           65535"

/etc/security/limits.d/90-nproc.conf:
  file.append:
    - text:
      - "*        -    nproc           65535"

selinux:
  cmd.run:
    - names:
      - sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
    - unless: grep 'SELINUX=disabled' /etc/selinux/config

iptables:
  cmd.run:
    - names:
      - chkconfig iptables off && service iptables stop
    - onlyif: chkconfig --list|grep iptables|grep on
