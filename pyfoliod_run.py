from webservice.app import the_app
from webservice.celery_task import celery

if __name__ == '__main__':
    the_app.run()

