from rest_framework import serializers
from ...models import Task
from accounts.models import Profile

class TaskSerializer(serializers.ModelSerializer):
    snippet_description = serializers.ReadOnlyField(source='get_snippet_desc')
    task_absolute_url = serializers.SerializerMethodField() 
    
    class Meta:
        model = Task
        fields = ['id', 'profile', 'title', 'snippet_description', 'description', 'done', 'created_date', 'task_absolute_url']
        read_only_fields = ['profile',]

        
# overriding the fields that shown for list and single task 
    def to_representation(self, instance):
    
        request = self.context.get('request')
        rep = super().to_representation(instance)
        if request.parser_context.get('kwargs').get('pk'):
            rep.pop('snippet_description', None) 
            rep.pop('task_absolute_url', None)
        else:
            rep.pop('description', None)
        return rep
    
    def create(self, validated_data):
        validated_data['profile']= Profile.objects.get(user__id = self.context.get('request').user.id)
        return super().create(validated_data)

 # getting a single task full url from request   
    def get_task_absolute_url(self, instance):
        request = self.context.get('request')
        return  request.build_absolute_uri(instance.pk)