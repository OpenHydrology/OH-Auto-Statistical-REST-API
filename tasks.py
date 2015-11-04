from core import celery, app
import autostatistical


@celery.task(bind=True)
def do_analysis(self, catchment_file):
    """Background OH Auto Statistical analysis task."""
    message = ''
    self.update_state(state='PROGRESS')

    analysis = autostatistical.Analysis(catchment_file)
    analysis.run()

    return {'message': message,
            'result': "OH Auto Statistical Report"}