jdk_user:
  user.present:
    - name: bestpay
    - uid: 1024
    - createhome: True
    - gid_from_name: True
    - shell: /bin/bash
    - password: $1$PnMSDXN4$.wDJrjsTqVPBn2HHzvnEe0
    - enforce_password: False


jdk_source:
  file.managed:
    - name: /tmp/jdk-7u65-linux-x64.tar.gz
    - unless: test -e /tmp/jdk-7u65-linux-x64.tar.gz
    - source: salt://jdk/files/jdk-7u65-linux-x64.tar.gz
 
  cmd.run:
    - names:
      - tar zxf /tmp/jdk-7u65-linux-x64.tar.gz -C /tools
    - unless: test -d /tools/jdk1.7.0_65   
    - require:
      - file: /tmp/jdk-7u65-linux-x64.tar.gz
     
/tools/jdk1.7.0_65:
  file.directory:
    - user: bestpay
    - group: bestpay
    - file_mode: 644
    - dir_mode: 755
    - recurse:
      - user
      - group
      - mode
    - require:
      - user: bestpay

/home/bestpay/.bash_profile:
  file.append:
    - text:
      - "export JAVA_HOME=/tools/jdk1.7.0_65"
      - "export PATH=$JAVA_HOME/bin:$PATH"
      - "export CLASSPATH=.:$CLASSPATH:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar"
