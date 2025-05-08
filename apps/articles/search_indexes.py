from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Article, Category, Tag


@registry.register_document
class ArticleDocument(Document):
    author = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "username": fields.TextField(),
        }
    )
    category = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
        }
    )
    tags = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
        }
    )
    publish_time = fields.DateField()

    class Index:
        name = "articles"  # Elasticsearch中的索引名称
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Article  # 关联的Django模型
        fields = [
            "title",
            "content",
        ]
        # 当关联的 Category 或 Tag 发生变化时，也更新索引
        related_models = [Category, Tag]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the instance(s) from the related model."""
        if isinstance(related_instance, Category):
            return related_instance.article_set.all()
        elif isinstance(related_instance, Tag):
            return (
                related_instance.article_set.all()
            )  # 假设 Article 和 Tag 是多对多关系，通过 article_set 反向查找

    def prepare_author(self, instance):
        if instance.author:
            return {"id": instance.author.id, "username": instance.author.username}
        return None

    def prepare_category(self, instance):
        if instance.category:
            return {"id": instance.category.id, "name": instance.category.name}
        return None

    def prepare_tags(self, instance):
        if instance.tags.exists():
            return [{"id": tag.id, "name": tag.name} for tag in instance.tags.all()]
        return []
