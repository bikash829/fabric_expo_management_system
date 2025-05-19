from pprint import pprint
from django.db import models

class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        # Only filter if model has is_deleted field
        if hasattr(self.model, 'is_deleted'):
            return self.filter(is_deleted=False)
        return self
    
    def soft_delete(self):
        for obj in self:
            obj.soft_delete()

    def restore(self):
        """Restore all soft-deleted objects in the queryset."""
        for obj in self:
            obj.is_deleted = False
            obj.save()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        qs = SoftDeleteQuerySet(self.model, using=self._db)
        # Only filter if model has is_deleted field
        if hasattr(self.model, 'is_deleted'):
            query_set = qs.filter(is_deleted=False)
            return query_set
        return qs
    
    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def only_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)
    

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, blank=True, editable=False)
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True