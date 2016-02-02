include:
    - users.useradd

dir:
  file.directory:
    - user: bestpay
    - group: bestpay
    - mode: 755
    - makedirs: True
    - unless: test -d /tools
    - require:
      - user: bestpay
