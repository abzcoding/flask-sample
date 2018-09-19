from celery import Celery

celery = Celery()


@celery.task
def sample():
  return "something"
