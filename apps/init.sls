include:
    - jetty.install
    - user.useradd
    - dirs.init

app_file:
  file.managed:
    - name: /tools/jetty/webapps/index.jsp
    - source: salt://apps/files/index.jsp
    - user: bestpay
    - group: bestpay

