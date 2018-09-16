from celery import Celery
from datetime import datetime

celery = Celery()

@celery.task
def sample():
  print(datetime.utcnow())
