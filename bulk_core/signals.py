from django.db.models.signals import pre_delete
from django.dispatch import receiver
import logging


logger = logging.getLogger(__name__)

from bulk_core.models import TempRecipientDataSheet

@receiver(pre_delete, sender=TempRecipientDataSheet)
def delete_data_sheet_file(sender, instance, **kwargs):
    if instance.data_sheet:
        logger.info(f"[Signal] Deleting file: {instance.data_sheet.path}")
        instance.data_sheet.delete(save=False)  # deletes file from storage
