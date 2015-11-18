from core import celery, db
import autostatisticalweb
from floodestimation import parsers
from glob import glob
import os.path
import shutil


@celery.task(bind=True)
def do_analysis(self, catchment_str, catchment_ext, amax_str=None):
    """
    Background OH Auto Statistical analysis task.

    :param catchment_str: Catchment file content
    :type catchment_str: str
    :param catchment_ext: Extension of catchment file (.xml or .cd3)
    :type catchment_ext: str
    :param amax_str: Amax file content
    :type amax_str: str
    :return: Dict with analysis report (Markdown) in `result` key.
    :rtype: dict
    """
    try:
        db_session = db.Session()
        parser_by_ext = {
            '.cd3': parsers.Cd3Parser,
            '.xml': parsers.XmlCatchmentParser
        }
        catchment = parser_by_ext[catchment_ext]().parse_str(catchment_str)
        if amax_str:
            catchment.amax_records = parsers.AmaxParser().parse_str(amax_str)
        analysis = autostatisticalweb.Analysis(catchment, db_session)
        result = analysis.run()

        return {'message': '', 'result': result}
    except Exception as e:
        raise  # Celery handles errors
    finally:
        if db_session:
            db_session.close()
