from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'avatar', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'bio']

    def validate(self, attrs):
        """验证密码是否匹配"""
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "两次密码输入不一致"})
        return attrs

    def create(self, validated_data):
        """创建用户"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            bio=validated_data.get('bio', '')
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'avatar']
