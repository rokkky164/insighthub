from django.db.models import Model, QuerySet
from typing import Type, List, Tuple


class BaseModelManager:
    model: Type[Model] = None

    @classmethod
    def _check_model(cls):
        if cls.model is None:
            raise NotImplementedError("Model class is not set for the Manager")

    @classmethod
    def filter_by(cls, **kwargs) -> QuerySet:
        cls._check_model()
        return cls.model.objects.filter(**kwargs)

    @classmethod
    def get_by(cls, **kwargs) -> Model:
        cls._check_model()
        return cls.model.objects.get(**kwargs)

    @classmethod
    def create_object(cls, **kwargs) -> Model:
        cls._check_model()
        return cls.model.objects.create(**kwargs)

    @classmethod
    def get_all(cls) -> QuerySet:
        cls._check_model()
        return cls.model.objects.all()

    @classmethod
    def update_all(cls, objs: List[Model], fields: List[str]):
        cls._check_model()
        if not objs or not fields:
            raise ValueError("Both objs and fields must be provided.")
        return cls.model.objects.bulk_update(objs, fields)

    @classmethod
    def get_or_create(cls, **kwargs) -> Tuple[Model, bool]:
        cls._check_model()
        return cls.model.objects.get_or_create(**kwargs)

    @classmethod
    def update_by(cls, filters: dict, updates: dict):
        cls._check_model()
        return cls.model.objects.filter(**filters).update(**updates)

    @classmethod
    def delete_by(cls, **kwargs):
        cls._check_model()
        return cls.model.objects.filter(**kwargs).delete()