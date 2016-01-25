nginx_own:
  file.directory:
    - name: /tools/nginx
    - user: bestpay
    - group: bestpay
    - file_mode: 644
    - dir_mode: 755
    - recurse:
      - user
      - group
      - mode

{% for file in ['sbin/nginx','conf/nginx.conf','sites-enabled/status_vhosts.conf'] %}
{% if file == 'sbin/nginx' %}
/tools/nginx/{{ file }}:
  file.managed:
    - name: /tools/nginx/{{ file }}
    - mode: 755
  cmd.run:
    - names:
      - ln -s /tools/nginx/{{ file }} /{{ file }}
    - unless: ls /{{ file }}
{% elif file == 'conf/nginx.conf' %}
/tools/nginx/{{ file }}:
  file.managed:
    - name: /tools/nginx/{{ file }}
    - source: salt://nginx/files/nginx.conf
  cmd.run:
    - names:
      - ln -s /tools/nginx/{{ file }} /etc/nginx.conf
    - unless: ls /etc/nginx.conf
{% else %}
/tools/nginx/{{ file }}:
  file.managed:
    - name: /tools/nginx/{{ file }}
    - source: salt://nginx/files/status_vhosts.conf
{% endif %}
{% endfor %}

{% for dir in ['sites-enabled','ssl'] %}
/tools/nginx/{{ dir }}:
  file.directory:
    - makedirs: True
    - unless: test -d /tools/nginx/{{ dir }}
    - user: bestpay
    - group: bestpay
    - dir_mode: 755
    - recurse:
      - user
      - group
      - mode
{% endfor %}

