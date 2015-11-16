from core import celery, db
import autostatisticalweb
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
        db_session = db.Session()
        analysis = autostatisticalweb.Analysis(catchment_fp, db_session)
        result = analysis.run()

        return {'message': '', 'result': result}
    except Exception as e:
        raise  # Celery handles errors
    finally:
        if db_session:
            db_session.close()
        shutil.rmtree(work_folder)
