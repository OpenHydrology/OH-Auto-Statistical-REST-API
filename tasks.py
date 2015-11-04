from core import celery, app
import random
import time


@celery.task(bind=True)
def do_analysis(self, catchment_file):
    """Background OH Auto Statistical analysis task."""
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        self.update_state(state='PROGRESS',
                          meta={'message': message})
        time.sleep(1)
    return {'message': message,
            'result': "OH Auto Statistical Report"}