from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from typing import Type, Optional, Dict, Any, List, Union


class AbstractCRUD:
    model: Type[models.Model] = None
    
    @classmethod
    def validate_model_class(cls):
        """Validate that the model class is properly set."""
        if cls.model is None or not issubclass(cls.model, models.Model):
            raise ValueError(f"{cls.__name__} must define a valid Django model as 'model' attribute")
    
    @classmethod
    def create(cls, data: Dict[str, Any], commit: bool = True) -> models.Model:
        cls.validate_model_class()
        
        try:
            instance = cls.model(**data)
            if commit:
                instance.full_clean()
                instance.save()
            return instance
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Invalid data for {cls.model.__name__} creation: {str(e)}")
    
    @classmethod
    def get_by_id(cls, id: Union[int, str]) -> Optional[models.Model]:
        cls.validate_model_class()
        
        try:
            return cls.model.active_objects.get(pk=id)
        except (ObjectDoesNotExist, ValueError):
            return None
        except Exception as e:
            raise ValueError(f"Error retrieving {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def get_by_filters(cls, filters: Dict[str, Any]) -> models.QuerySet:
        cls.validate_model_class()
        
        try:
            return cls.model.active_objects.filter(**filters)
        except Exception as e:
            raise ValueError(f"Invalid filters for {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def get_all(cls) -> models.QuerySet:
        cls.validate_model_class()
        return cls.model.active_objects.all()
    
    @classmethod
    def update(
        cls,
        instance: models.Model,
        update_data: Dict[str, Any],
        commit: bool = True
    ) -> models.Model:
        cls.validate_model_class()
        
        if not isinstance(instance, cls.model):
            raise ValueError(f"Instance must be of type {cls.model.__name__}")
        
        try:
            for field, value in update_data.items():
                setattr(instance, field, value)
            
            if commit:
                instance.full_clean()  # Validate fields
                instance.save()
            
            return instance
        except (AttributeError, ValueError) as e:
            raise ValidationError(f"Invalid update data for {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def delete(cls, instance: models.Model, commit: bool = True) -> bool:
        cls.validate_model_class()
        
        if not isinstance(instance, cls.model):
            raise ValueError(f"Instance must be of type {cls.model.__name__}")
        
        try:
            if commit:
                instance.soft_delete()
            return True
        except Exception as e:
            raise ValueError(f"Error deleting {cls.model.__name__} instance: {str(e)}")
    
    @classmethod
    def bulk_create(
        cls,
        instances_data: List[Dict[str, Any]],
        batch_size: Optional[int] = None
    ) -> List[models.Model]:
        cls.validate_model_class()
        
        try:
            instances = [cls.model(**data) for data in instances_data]
            return cls.model.active_objects.bulk_create(instances, batch_size=batch_size)
        except Exception as e:
            raise ValueError(f"Bulk creation failed for {cls.model.__name__}: {str(e)}")
    
    @classmethod
    def bulk_update(
        cls,
        instances: List[models.Model],
        fields: List[str],
        batch_size: Optional[int] = None
    ) -> int:
        cls.validate_model_class()
        
        if not all(isinstance(instance, cls.model) for instance in instances):
            raise ValueError(f"All instances must be of type {cls.model.__name__}")
        
        try:
            return cls.model.active_objects.bulk_update(instances, fields, batch_size=batch_size)
        except Exception as e:
            raise ValueError(f"Bulk update failed for {cls.model.__name__}: {str(e)}")