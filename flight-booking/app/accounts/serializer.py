import re
from rest_framework import (
    serializers,
    validators
)
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    '''UserSerializer - to Validate User Sign Up'''
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(
        required=True,
    )
    last_name = serializers.CharField(
        required=True,
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True
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

    def validate_username(self, username):
        '''Validate username so it can only contain alphanumeric characters
        and few special characters like  `_` and `.`
        '''
        if re.search(r'([^a-zA-Z/._\d+])', username) is None:
            return username

        raise serializers.ValidationError(
            'Username can only contain alphanumeric characters and . or _.'
        )

    def validate_password(self, password):
        '''Validate password matches condition'''
        if re.search(r'(^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$_!%*?&]{8,}$)', password) is not None:
            return password
        raise serializers.ValidationError(
            'Must have at least 1 uppercase, 1 lowercase, 1 number and 1 special character'
        )

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user
