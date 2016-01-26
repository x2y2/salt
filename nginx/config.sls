include:
  - nginx.install

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
{% else %}
/tools/nginx/{{ file }}:
  file.managed:
    - name: /tools/nginx/{{ file }}
    - source: salt://nginx/files/{{ file.split('/')[1] }}
{% endif %}
{% endfor %}

/etc/nginx.conf:
  file.symlink:
    - target: /tools/nginx/conf/nginx.conf

/sbin/nginx:
  file.symlink:
    - target: /tools/nginx/sbin/nginx

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

