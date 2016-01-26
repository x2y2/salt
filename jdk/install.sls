include:
  - users.useradd

jdk_home:
  file.recurse:
    - name: /tools/java
    - source: salt://jdk/files/java
    - user: bestpay
    - group: bestpay
    - file_mode: 644
    - dir_mode: 755
    - include_empty: True
    - require:
      - user: bestpay

/home/bestpay/.bash_profile:
  file.append:
    - text:
      - "export JAVA_HOME=/tools/java"
      - "export PATH=$JAVA_HOME/bin:$PATH"
      - "export CLASSPATH=.:$CLASSPATH:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar"
