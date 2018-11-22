from rest_framework import (
    serializers,
    validators
)
from django.contrib.auth.models import User


class UserAuthSerializer(serializers.ModelSerializer):
    '''UserAuthSerializer -'''
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'username',
            'first_name',
            'last_name',
        )

    def validate_email(self, email):
        '''Validate email is a real one'''
        if re.search(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[a-zA-Z0-9]+$)'):
            return email
        return serializers.ValidationError(
            'Email address not valid'
        )

    def validate_password(self, password):
        '''Validate password matches condition'''
        if re.search(r'(^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$_!%*?&]{8,}$)'):
            return password
        return serializers.ValidationError(
            'Must have at least 1 uppercase, 1 lowercase, 1 number and 1 special character'
        )
