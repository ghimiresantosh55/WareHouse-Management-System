from django.contrib.auth import authenticate, get_user_model
# from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from src.core_app.setup_helper import check_setup
from src.custom_lib.functions import current_user
from src.department.models import Department
from src.user_group.models import CustomGroup, CustomPermission
from tenant.models import Tenant
from tenant.utils import tenant_schema_from_request

User = get_user_model()


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomGroup
        fields = "__all__"


class UserLoginPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = ['id', 'name', 'code_name']


class UserLoginGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomGroup
        fields = ['id', 'name']


class UserLoginDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class UserListSerializer(serializers.ModelSerializer):
    groups = UserLoginGroupsSerializer(many=True, read_only=True)
    departments = UserLoginDepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ['password', 'user_permissions']

    def to_representation(self, instance):
        my_fields = {'photo', 'birth_date', 'created_by', }
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    user_name = serializers.CharField(
        min_length=4, max_length=50, required=True, allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, min_length=6
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('user_name', 'password', 'confirm_password', 'email',
                  'first_name', 'last_name', 'middle_name', 'is_active', 'gender', 'birth_date',
                  'address', 'mobile_no', 'groups', 'photo', 'full_name', 'departments')
        read_only_fields = ['full_name', 'created_by', ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'groups': {'required': True},
            'departments': {'required': True},
        }

    def to_representation(self, instance):
        my_fields = {'birth_date'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass

        #  giving group name in group
        group_data = []
        groups = data['groups']
        for group in groups:
            group_data.append({
                "id": group,
                "name": CustomGroup.objects.get(id=group).name
            })
        data['groups'] = group_data
        return data

    def validate_password(self, password):
        if len(password) < 6:
            serializers.ValidationError("Password must be at least 6 characters")
        if len(password) > 32:
            serializers.ValidationError("password must be max 32 characters")
        if str(password).isalpha():
            serializers.ValidationError("password must contain at least alphabets and numbers")
        return password

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers \
                .ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_user_name(self, value):
        small_case_value = value.lower()
        if small_case_value != value:
            raise serializers.ValidationError(
                {"user_name": "username does not support Uppercase Letters."})
        if " " in value:
            raise serializers.ValidationError(
                {"user_name": "username does not support blank character."})
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['created_by'] = current_user.get_created_by(self.context)
        groups_data = validated_data.pop('groups')
        departments = validated_data.pop('departments')
        user = User.objects.create_user(**validated_data)
        for group_data in groups_data:
            user.groups.add(group_data)
        for department in departments:
            user.departments.add(department)
        user.save()

        return user


class LoginSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(max_length=50, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=4, write_only=True
    )
    tokens = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    is_setup_done = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user_name', 'password',
                  'groups', 'tokens', 'is_superuser', 'photo', 'permissions', 'is_setup_done', 'branch_name']
        read_only_fields = ['groups', 'is_superuser', 'photo', 'is_setup_done',
                            'full_name', 'permissions', 'branch_name']

    def validate(self, attrs):
        # request = self.context.get('request')
        user_name = attrs.get('user_name', '')
        password = attrs.get('password', '')
        user = authenticate(user_name=user_name, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            'user_name': user.user_name,
            'id': user.id,
            'is_superuser': user.is_superuser,
            'photo': user.photo,
            'full_name': user.full_name,

        }

    @staticmethod
    def get_is_setup_done(attrs):
        return check_setup()

    def get_tokens(self, obj):
        user = User.objects.get(user_name=obj['user_name'])
        request = self.context.get('request', None)
        user_tokens = user.tokens(request)
        return {
            # 'refresh': user.tokens(request)['refresh'],
            'refresh': user_tokens['refresh'],
            # 'access': user.tokens(request)['access']
            'access': user_tokens['access']
        }

    def get_groups(self, attrs):
        user = User.objects.get(user_name=attrs['user_name'])
        groups = user.groups.filter(is_active=True)
        serializer = UserLoginGroupsSerializer(groups, many=True)
        return serializer.data

    def get_permissions(self, attrs):
        user = User.objects.get(user_name=attrs['user_name'])
        groups = user.groups.filter(is_active=True).values_list('id', flat=True)
        permissions = CustomPermission.objects.filter(customgroup__in=groups)
        serializer = UserLoginPermissionSerializer(permissions, many=True)
        return serializer.data

    def get_branch_name(self, obj):
        tenant = Tenant.objects.get(schema_name=tenant_schema_from_request(self.context['request']))
        return tenant.name


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except:
            raise serializers.ValidationError({"bad token"})


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'confirm_password')
        extra_kwargs = {
            'old_password': {'required': True},
            'password': {'required': True},
            'confirm_password': {'required': True}
        }

    def validate_password(self, password):
        if len(password) < 6:
            serializers.ValidationError("Password must be at least 6 characters")
        if len(password) > 32:
            serializers.ValidationError("password must be max 32 characters")
        if str(password).isalpha():
            serializers.ValidationError("password must contain at least alphabets and numbers")
        return password

    def validate(self, attrs):
        user = self.context['request'].user
        try:
            if not user.check_password(attrs['old_password']):
                raise serializers \
                    .ValidationError(
                    {"old_password": "Old password is not correct"}
                )
        except KeyError:
            raise serializers.ValidationError(
                {'key_error': 'please provide old_password'})

        try:
            if attrs['password'] != attrs['confirm_password']:
                raise serializers \
                    .ValidationError({"password": "Password fields didn't match."})
        except KeyError:
            raise serializers.ValidationError(
                {'key_error': 'please provide password and confirm_password'})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    user_name = serializers.CharField(required=True)

    # user_group_name = serializer.ReadOnlyField(
    #     source='group.name', allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'middle_name', 'last_name', 'email', 'user_name', 'is_active',
                  'gender', 'birth_date', 'address', 'mobile_no', 'photo', 'groups', 'departments')
        read_only_fields = ['id']

    def validate_email(self, value):
        pk = self.context['pk']
        if User.objects.exclude(pk=pk).filter(email=value).exists():
            raise serializers.ValidationError(
                {"email": "This email is already in use."})
        return value

    def validate_user_name(self, value):
        pk = self.context['pk']
        if User.objects.exclude(pk=pk).filter(user_name=value).exists():
            raise serializers.ValidationError(
                {"user_name": "This username is already in use."})
        small_case_value = value.lower()
        if small_case_value != value:
            raise serializers.ValidationError(
                {"user_name": "username does not support Uppercase Letters."})
        if " " in value:
            raise serializers.ValidationError(
                {"user_name": "username does not support blank character."})
        return value


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = "__all__"
