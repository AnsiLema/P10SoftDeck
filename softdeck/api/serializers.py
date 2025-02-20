from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Project, Contributor, Issue, Comment
from django.contrib.auth import get_user_model


# ---------------------- USER SERIALIZERS ----------------------- #

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
        """
        Creates and returns a new `CustomUser` instance.

        This method is utilized to create a new user in the system by delegating
        the user creation logic to the `CustomUser.objects.create_user` method.
        All relevant user data should be passed in via the `validated_data` dictionary.

        :param validated_data: Dictionary containing validated data needed for user creation.
        :return: An instance of the newly created `CustomUser`.
        :rtype: CustomUser
        """
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """
        Updates an instance of the user model with the provided validated data. The function will
        update the following fields if they are present in validated_data: 'username', 'email',
        'birth_date', 'can_be_contacted', 'can_data_be_shared', and 'password'. If 'password' is
        present in the validated_data, the password will be properly hashed before saving. After
        updating the instance with the provided data, it is saved back to the database.

        :param instance:
            Instance of the user model to be updated.
        :param validated_data:
            Dictionary containing the data to update the user instance. Accepted keys are
            'username', 'email', 'birth_date', 'can_be_contacted', 'can_data_be_shared', and
            'password'.
        :return:
            The updated instance of the user model.
        """
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.birth_date = validated_data.get("birth_date", instance.birth_date)
        instance.can_be_contacted = validated_data.get("can_be_contacted", instance.can_be_contacted)
        instance.can_data_be_shared = validated_data.get("can_data_be_shared", instance.can_data_be_shared)

        if "password" in validated_data:
            instance.set_password(validated_data["password"])

        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing a list of CustomUser objects.

    This class is a subclass of ModelSerializer from Django REST framework.
    It is used to serialize and deserialize data for the CustomUser model,
    allowing control over which model fields are included in the serialized
    output. The fields specified in this serializer include `id`, `username`,
    and `email`.

    :cvar model: Specifies the model to be serialized.
    :type model: type
    :cvar fields: Specifies the fields of the model to be included in the
        serialized output.
    :type fields: tuple
    """
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')


# ---------------------- PROJECT SERIALIZERS ----------------------- #

class ProjectListSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Project
        fields = ('id', 'title', 'author')

    def validate_project_title(self, value):
        """ Checks if the project title is unique """
        if Project.objects.filter(title=value).exists():
            raise serializers.ValidationError("Un projet portant ce nom existe déja.")
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'type', 'author')


# -------------------- CONTRIBUTOR SERIALIZER ---------------------- #

class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Contributor
        fields = ('id', 'user', 'project')

# ------------------------ ISSUE SERIALIZER ------------------------- #

class IssueDetailSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Issue
        fields = ('id', 'title', 'description', 'priority', 'tag', 'status',
                  'project', 'assigned_to', 'author', 'created_time')


class IssueListSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Issue
        fields = ('id', 'title', 'priority', 'tag', 'status',)

# ------------------------ COMMENT SERIALIZER ------------------------- #


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = Comment
        fields = ('id', 'description', 'author', 'issue', 'created_time')


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = Comment
        fields = ('id', 'description', 'author')