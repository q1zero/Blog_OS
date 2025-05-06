from rest_framework import serializers
from apps.comments.models import Comment


class RecursiveCommentSerializer(serializers.Serializer):
    """递归评论序列化器，用于嵌套评论"""
    def to_representation(self, instance):
        serializer = CommentSerializer(instance, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    replies = RecursiveCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'author', 'author_id', 'content', 
            'parent', 'replies', 'created_at', 'is_approved'
        ]
        read_only_fields = ['id', 'author', 'author_id', 'created_at', 'is_approved']


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""
    class Meta:
        model = Comment
        fields = ['article', 'content', 'parent']
    
    def validate_parent(self, value):
        """验证父评论"""
        if value and value.article.id != self.initial_data.get('article'):
            raise serializers.ValidationError("父评论必须属于同一篇文章")
        return value
