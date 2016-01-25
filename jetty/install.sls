jetty_user:
  user.present:
    - name: bestpay
    - uid: 1024
    - createhome: True
    - gid_from_name: True
    - shell: /bin/bash
    - password: $1$PnMSDXN4$.wDJrjsTqVPBn2HHzvnEe0
    - enforce_password: False

jetty_source:
  file.managed:
    - name: /tmp/jetty-distribution-8.1.17.v20150415.tar.gz
    - unless: －e /tmp/jetty-distribution-8.1.17.v20150415.tar.gz
    - source: salt://jetty/files/jetty-distribution-8.1.17.v20150415.tar.gz

  cmd.run:
    - names:
      - tar zxf /tmp/jetty-distribution-8.1.17.v20150415.tar.gz -C /tools && mv /tools/jetty-distribution-8.1.17.v20150415 /tools/jetty
    - unless: test -d /tools/jetty
    - require:
      - file: /tmp/jetty-distribution-8.1.17.v20150415.tar.gz

config_file:  
  file.managed:
    - name: /tools/jetty/etc/jetty.xml
    - source: salt://jetty/files/jetty.xml

log_file:
  file.managed:
    - name: /tools/jetty/etc/jetty-logging.xml
    - source: salt://jetty/files/jetty-logging.xml

jetty_script:
  file.managed:
    - name: /tools/jetty/bin/jetty.sh
    - source: salt://jetty/files/jetty.sh
    - mode: 755

context_file:
  file.managed:
    - name: /tools/jetty/contexts/test.xml
    - source: salt://jetty/files/test.xml

/tools/jetty:
  file.directory:
    - user: bestpay
    - group: bestpay
    - recurse:
      - user
      - group
    - require:
      - user: bestpay
