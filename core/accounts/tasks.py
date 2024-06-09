from celery import shared_task
from time import sleep


@shared_task
def test():
    sleep(10)
    print("hello world")
