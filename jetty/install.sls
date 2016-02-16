jetty_home:
  file.recurse:
    - name: /tools/jetty
    - source: salt://jetty/files/jetty
    - user: bestpay
    - group: bestpay
    - dir_mode: 755
    - include_empty: True
    - require:
      - user: bestpay

jetty_bin:
  file.managed:
      - name: /tools/jetty/bin/jetty.sh
      - mode: 755
      - require:
        - file: /tools/jetty
