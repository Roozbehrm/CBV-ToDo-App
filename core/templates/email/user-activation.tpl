{% extends "mail_templated/base.tpl" %}

{% block subject %}
Account Activation 
{% endblock %}


{% block html %}
{{link}} </br>
<a href="{{link}}">Activate Account</a>
{% endblock %}