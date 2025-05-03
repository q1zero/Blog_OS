from rest_framework import serializers
from apps.articles.models import Article, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class ArticleListSerializer(serializers.ModelSerializer):
    """文章列表序列化器"""
    author = serializers.ReadOnlyField(source='author.username')
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'tags', 
            'status', 'visibility', 'created_at', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'published_at']


class ArticleDetailSerializer(serializers.ModelSerializer):
    """文章详情序列化器"""
    author = serializers.ReadOnlyField(source='author.username')
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'author', 'category', 'tags', 
            'status', 'visibility', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'published_at']


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """文章创建和更新序列化器"""
    category_id = serializers.IntegerField(required=False, allow_null=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'category_id', 'tag_ids', 
            'status', 'visibility'
        ]
    
    def validate_category_id(self, value):
        """验证分类ID"""
        if value is not None:
            try:
                Category.objects.get(id=value)
            except Category.DoesNotExist:
                raise serializers.ValidationError("指定的分类不存在")
        return value
    
    def validate_tag_ids(self, value):
        """验证标签ID列表"""
        if value:
            existing_tags = Tag.objects.filter(id__in=value)
            if len(existing_tags) != len(value):
                raise serializers.ValidationError("部分标签不存在")
        return value
    
    def create(self, validated_data):
        """创建文章"""
        tag_ids = validated_data.pop('tag_ids', [])
        category_id = validated_data.pop('category_id', None)
        
        # 创建文章
        article = Article.objects.create(
            **validated_data,
            category_id=category_id
        )
        
        # 添加标签
        if tag_ids:
            article.tags.set(tag_ids)
        
        return article
    
    def update(self, instance, validated_data):
        """更新文章"""
        tag_ids = validated_data.pop('tag_ids', None)
        category_id = validated_data.pop('category_id', None)
        
        # 更新文章字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 更新分类
        if category_id is not None:
            instance.category_id = category_id
        
        # 更新标签
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        
        instance.save()
        return instance
