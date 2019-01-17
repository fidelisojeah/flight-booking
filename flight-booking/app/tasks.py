from celery.decorators import task


@task(name='sample_celery_command')
def sample_celery_command(x, y):
    return x + y
