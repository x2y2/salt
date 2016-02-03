include:
    - users.useradd

/tools/script/logbackup:
  file.directory:
    - user: bestpay
    - group: bestpay
    - mode: 755
    - makedirs: True
    - require:
      - user: bestpay

app_logbackup:
  file.managed:
    - source: salt://scripts/files/app_logback.py
    - name: /tools/script/logbackup/app_logback.py
    - user: bestpay
    - group: bestpay
    - mode: 755
    - template: jinja
