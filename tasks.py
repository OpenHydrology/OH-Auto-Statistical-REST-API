from core import celery, db
import autostatisticalweb
from floodestimation import parsers
from floodestimation import entities


@celery.task(bind=True)
def do_analysis(self, catchment_str, amax_str=None):
    """
    Background OH Auto Statistical analysis task.

    :param catchment_str: Catchment file content (either in xml or cd3 format)
    :type catchment_str: str
    :param amax_str: Amax file content
    :type amax_str: str
    :return: Dict with analysis report (Markdown) in `result` key.
    :rtype: dict
    """
    self.update_state(state='PROGRESS', meta={'message': ''})
    try:
        db_session = db.Session()
        parser_by_ext = {
            '.cd3': parsers.Cd3Parser,
            '.xml': parsers.XmlCatchmentParser
        }
        ext = '.xml' if is_xml(catchment_str) else '.cd3'
        catchment = parser_by_ext[ext]().parse_str(catchment_str)
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


@celery.task(bind=True)
def do_analysis_from_id(self, catchment_id):
    """
    Background OH Auto Statistical analysis task using a catchment from the database.

    :param catchment_id: Catchment id (NRFA gauging station no.)
    :type catchment_id: int
    :return: Dict with analysis report (Markdown) in `result` key.
    :rtype: dict
    """
    self.update_state(state='PROGRESS', meta={'message': ''})
    try:
        db_session = db.Session()
        catchment = db_session.query(entities.Catchment).get(catchment_id)
        if catchment is None:
            raise ValueError("Catchment with id `{}` does not exist.".format(catchment_id))
        analysis = autostatisticalweb.Analysis(catchment, db_session)
        result = analysis.run()

        return {'message': '', 'result': result}
    except Exception as e:
        raise  # Celery handles errors
    finally:
        if db_session:
            db_session.close()


def is_xml(s):
    """
    Returns whether a string is xml

    :param s: string to test
    :type s: str
    :return: True if string is xml
    :rtype: bool
    """
    return s.startswith('<')