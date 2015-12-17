from core import celery, db
import autostatisticalweb
from floodestimation import parsers
from floodestimation import entities
from floodestimation import loaders
import os.path
import requests
import tempfile
import zipfile
import logging


logger = logging.getLogger(__name__)


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
    assert isinstance(catchment_id, int)
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


@celery.task(bind=True, ignore_result=True)
def import_data(self, from_url):
    """
    Imports catchment and annual maximum flow data into the database

    :param from_url: URL to pull data from (only zip files supported)
    :type from_url: str
    """
    self.update_state(state='PROGRESS', meta={'message': ''})
    assert from_url.lower().endswith('.zip')
    logger.info("Starting to import from url {}".format(from_url))
    try:
        db_session = db.Session()
        data_fn = 'data.zip'
        r = requests.get(from_url, stream=True)
        with tempfile.TemporaryDirectory() as work_folder:
            with open(os.path.join(work_folder, data_fn), 'wb') as data_f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        data_f.write(chunk)
            logger.info("Data downloaded to {}".format(os.path.join(work_folder, data_fn)))

            with zipfile.ZipFile(os.path.join(work_folder, data_fn), 'r') as data_f:
                cd3_and_am = [m for m in data_f.infolist()
                              if os.path.splitext(m.filename)[1].lower() in ['.cd3', '.am']]
                for member in cd3_and_am:
                    member.filename = os.path.basename(member.filename)  # strip folder info, extract all files to root
                    data_f.extract(member, path=work_folder)
            logger.info("{} Files extracted to {}".format(len(cd3_and_am), work_folder))

            loaders.folder_to_db(work_folder, db_session, method='update', incl_pot=False)
            logger.info("Catchment files parsed")
            db_session.commit()
            logger.info("Catchments committed to database")

    except Exception as e:
        db_session.rollback()
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