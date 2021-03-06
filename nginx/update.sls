{% for file in ['nginx-1.8.0.tar.gz','openssl-1.0.2d.tar.gz','pcre-8.37.tar.gz','zlib-1.2.8.tar'] %}
transfer_{{ file }}:
  file.managed:
    - name: /tmp/{{ file }}
    - source: salt://nginx/files/{{ file }}
    - unless: -e /tmp/{{ file  }}
{% endfor %}

{% for file in ['nginx-1.8.0','openssl-1.0.2d','pcre-8.37','zlib-1.2.8'] %}
{% if file == 'zlib-1.2.8' %}
uncompress_{{ file }}:
  cmd.run:
    - cwd: /tmp
    - names:
      - tar xf /tmp/{{ file }}.tar
    - unless: test -d /tmp/{{ file }}.tar
{% else %}
uncompress_{{ file }}:
  cmd.run:
    - cwd: /tmp
    - names:
      - tar zxf /tmp/{{ file }}.tar.gz
    - unless: test -d /tmp/{{ file }}
{% endif %}
{% endfor %}

nginx_install:
  cmd.run:
    - cwd: /tmp/nginx-1.8.0
    - names:
      - ./configure --prefix=/tools/nginx --with-http_stub_status_module --with-zlib=../zlib-1.2.8 --with-pcre=../pcre-8.37 --with-openssl=../openssl-1.0.2d
      - make
      - mv /tools/nginx/sbin/nginx /tools/nginx/sbin/nginx.old
      - cp objects/nginx /tools/nginx/sbin/nginx
      - make upgrade
