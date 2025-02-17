from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    Represents a serializer for the User model to handle the conversion between
    complex data types such as instances or querysets and native Python data
    types suitable for rendering into JSON or other content types.

    This serializer provides automatic field generation based on the model's
    fields and allows additional customization for validation, serialization,
    and deserialization of user data.

    :ivar model: The model class that the serializer is associated with. This defines
        the structure of the data to serialize/deserialize.
    :type model: Type[models.Model]
    :ivar fields: The fields of the model that should be included in the serializer.
        This allows selective inclusion of fields for representation and validation.
    :type fields: list[str]
    """

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'birth_date', 'can_be_contacted', 'can_data_be_shared')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.birth_date = validated_data.get("birth_date", instance.birth_date)
        instance.can_be_contacted = validated_data.get("can_be_contacted", instance.can_be_contacted)
        instance.can_data_be_shared = validated_data.get("can_data_be_shared", instance.can_data_be_shared)

        if "password" in validated_data:
            instance.set_password(validated_data["password"])

        instance.save()
        return instance
