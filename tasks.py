from core import celery, app
import autostatistical
from glob import glob
import os.path
import shutil


@celery.task(bind=True)
def do_analysis(self, catchment_fp):
    """Background OH Auto Statistical analysis task."""
    work_folder = os.path.dirname(catchment_fp)
    # self.update_state(state='PROGRESS')

    try:
        analysis = autostatistical.Analysis(catchment_fp)
        analysis.run()
        # TODO: make autostatistical output a string instead of write to file.
        # TOOD: reimplement autostatistical here to have greater flexibility on outputs (json, markdown, csv?).

        # For just now:
        result_fp = glob(os.path.join(work_folder, '*.md'))[0]
        with open(result_fp, encoding='utf-8') as result_f:
            result = result_f.read()
        return {'message': '', 'result': result}
    except Exception as e:
        return {'message': str(e)}
    finally:
        shutil.rmtree(work_folder)
