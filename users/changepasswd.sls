{% set users = ['bestpay','logview'] %}
{% for user in users %}
{{ user }}:
{% if user == 'bestpay' %}
  user.present:
    - shell: /bin/bash
    - password: '$1$w7lY9jKa$2peosTgcGVVALrhMVAgZG.'
{% endif %}
{% if user == 'logview' %}
  user.present:
    - shell: /bin/bash
    - password: '$1$AAInfttE$85g1CdaGxLdw6XSCqqi.j0'
{% endif%}
{% endfor %}
