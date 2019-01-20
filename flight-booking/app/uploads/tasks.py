import cloudinary

from celery import (shared_task, decorators)


@decorators.task(name='remove_profile_picture_cloudinary',
                 bind=True,
                 default_retry_delay=60 * 60,
                 retry_kwargs={'max_retries': 3})
def remove_profile_picture(self, public_id=None):
    '''REMOVE Uploaded CLOUDINARY Image'''
    if public_id is not None:
        try:
            cloudinary.uploader.destroy(public_id)
        except api.Error as exc:
            self.retry(exc=exc)
