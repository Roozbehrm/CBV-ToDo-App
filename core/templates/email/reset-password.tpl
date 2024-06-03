{% extends "mail_templated/base.tpl" %}

{% block subject %}
Reset Password
{% endblock %}


{% block html %}
{{link}} </br>
<a href="{{link}}">Reset Password</a>
{% endblock %}