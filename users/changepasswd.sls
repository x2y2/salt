include:
  - users.useradd

{% set users = ['bestpay','logview'] %}
{% for user in users %}
{% if user == 'bestpay' %}
{{ user }}:
  user.present:
    - shell: /bin/bash
    - password: '$1$w7lY9jKa$2peosTgcGVVALrhMVAgZG.'
{% else %}
{{ user }}:
  user.present:
    - shell: /bin/bash
    - password: '$1$AAInfttE$85g1CdaGxLdw6XSCqqi.j0'
{% endif%}
{% endfor %}
