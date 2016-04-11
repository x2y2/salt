/tools/script/logbackup:
  file.directory:
    - user: bestpay
    - group: bestpay
    - mode: 755
    - makedirs: True

app_logbackup:
  file.managed:
    - source: salt://scripts/files/test.sh
    - name: /tools/script/test.sh
    - user: bestpay
    - group: bestpay
    - mode: 755
