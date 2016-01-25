app_file:
  file.managed:
    - name: /tools/jetty/webapps/index.jsp
    - source: salt://apps/files/index.jsp
    - user: bestpay
    - group: bestpay

