from core import celery
import autostatistical
from glob import glob
import os.path
import shutil


@celery.task(bind=True)
def do_analysis(self, catchment_fp):
    """
    Background OH Auto Statistical analysis task.

    :param catchment_fp: Filepath for catchment file
    :type catchment_fp: str
    :return: Dict with analysis report (Markdown) in `result` key.
    :rtype: dict
    """
    work_folder = os.path.dirname(catchment_fp)

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
        raise  # Celery handles errors
    finally:
        shutil.rmtree(work_folder)
