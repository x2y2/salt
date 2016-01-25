nginx_user:
  user.present:
    - name: bestpay
    - uid: 1024
    - createhome: True
    - gid_from_name: True
    - shell: /bin/bash
    - password: $1$PnMSDXN4$.wDJrjsTqVPBn2HHzvnEe0
    - enforce_password: False

{% for file in ['nginx-1.8.0.tar.gz','openssl-1.0.2d.tar.gz','pcre-8.37.tar.gz','zlib-1.2.8.tar'] %}
transfer_{{ file }}:
  file.managed:
    - name: /tmp/{{ file }}
    - source: salt://nginx/files/{{ file }}
    - unless: -e /tmp/{{ file  }}
{% endfor %}

{% for file in ['nginx-1.8.0','openssl-1.0.2d','pcre-8.37','zlib-1.2.8'] %}
{% if file == 'zlib-1.2.8.tar' %}
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
      - ./configure --prefix=/tools/nginx --with-http_sub_module --with-zlib=../zlib-1.2.8 --with-pcre=../pcre-8.37 --with-openssl=../openssl-1.0.2d
      - make
      - make install
    - unless: test -d /tools/nginx

nginx_bin:
  cmd.run:
    - names:
      - ln -s /tools/nginx/sbin/nginx /sbin/nginx
    - unless: ls /sbin/nginx

nginx_conf:
  cmd.run:
    - names:
      - ln -s /tools/nginx/conf/nginx.conf /etc/nginx.conf
    - unless: ls /etc/nginx.conf
