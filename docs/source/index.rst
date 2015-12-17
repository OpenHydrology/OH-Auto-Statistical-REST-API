OH Auto Statistical web API
===========================

Version |version|


.. _api/doc:


Analyses
--------

.. http:post:: /api/v0/analyses/
    :synopsis: Submits an OH Auto Statistical analysis.

    Submits an OH Auto Statistical analysis to be undertaken asynchronously. Returns a ``Location`` header with a URL to
    retrieve the analysis task status.

    :form (any): ``.xml`` catchment file
    :form (any): ``.am`` annual maximum flow data file (optional)

    :resheader Content-Type: :mimetype:`application/json`
    :resheader Location: URL to retrieve task status

    :statuscode 202: Analysis task accepted
    :statuscode 400: Uploaded files invalid

    **Request**:

    .. code-block:: http

        POST /api/v0/analyses/ HTTP/1.0
        Accept: */*
        Host: localhost:5000

    **Response**:

    .. code-block:: http

        HTTP/1.0 202 ACCEPTED
        Content-Type: application/json
        Content-Length: 3
        Location: http://localhost:5000/api/v0/analysis-tasks/124cce24-b02f-4ad8-9475-e8826fb4e655
        Server: Werkzeug/0.10.4 Python/3.4.3
        Date: Thu, 05 Nov 2015 17:45:04 GMT

.. http:get:: /api/v0/analyses/(task_id)
    :synopsis: Returns an OH Auto Statistical analysis.

    Returns the OH Auto Statistical analysis report as Markdown-formatted text using the completed task's ``task_id``.
    Note that this endpoint does not need to be called explicitly as the task status will redirect to here.

    :param task_id: Task identifier

    :resheader Content-Type: - :mimetype:`text/plain; charset=utf-8` (analysis report)
                             - :mimetype:`application/json` (error message)

    :statuscode 200: Report successfully returned
    :statuscode 404: Not a completed analysis task for ``task_id``

    **Response**:

    .. code-block:: http

        HTTP/1.0 200 OK
        Content-Type: text/plain; charset=utf-8
        Content-Length: 6412
        Server: Werkzeug/0.10.4 Python/3.4.3
        Date: Thu, 05 Nov 2015 19:16:01 GMT

        # Flood Estimation Report

        Date:          05/11/2015
        Software:      OH Auto Statistical version 0.8.0

        ## Input data

        River:         Urr
        (...)


Analysis tasks
--------------

.. http:get:: /api/v0/analysis-tasks/(task_id)
    :synopsis: Returns the analysis status or redirects to the analysis report when completed

    If the analysis task is not yet completed the task's status is returned (json). Otherwise redirects to the analysis
    report itself.

    :param task_id: Task identifier

    :resheader Content-Type: :mimetype:`application/json`
    :resheader Location: URL to retrieve task results (when completed)

    :statuscode 200: Status successfully returned
    :statuscode 303: Redirect to ``/api/v0/analyses/(task_id)``

    **Request**:

    .. code-block:: http

        GET api/v0/analysis-tasks/124cce24-b02f-4ad8-9475-e8826fb4e655 HTTP/1.0
        Accept: */*
        Host: localhost:5000

    **Response (task in progress)**:

    .. code-block:: http

        HTTP/1.0 200 OK
        Content-Type: application/json
        Content-Length: 56
        Server: Werkzeug/0.10.4 Python/3.4.3
        Date: Thu, 05 Nov 2015 20:06:26 GMT

        {
            "message": "",
            "state": "PROGRESS"
        }

    **Response (task completed)**:

    .. code-block:: http

        HTTP/1.0 303 OK
        Content-Type: application/json
        Content-Length: 3
        Location: http://localhost:5000/api/v0/analysis/124cce24-b02f-4ad8-9475-e8826fb4e655
        Server: Werkzeug/0.10.4 Python/3.4.3
        Date: Thu, 05 Nov 2015 20:06:30 GMT


Data imports
------------

.. http:post:: /api/v0/data-imports/
    :synopsis: Update peak flow data from URL

    Load new data into the peak flow database by providing a URL for a zip file of .cd3 and .am files. The zip file is
    retrieved and files are parsed and then inserted (update) into the database.

    :reqheader Content-Type: :mimetype:`application/json`
    :reqheader Authorization: Valid bearer token for authentication

    :statuscode 202: Import task accepted
    :statuscode 400: Invalid request body
    :statuscode 401: Missing or invalid bearer token

    **Request**:

    .. code-block:: http

        POST /api/v0/data-imports/ HTTP/1.0
        Accept: */*
        Authorization: Bearer secrettoken
        Content-Type: application/json
        Host: localhost:5000

        {
            "url": "https://github.com/OpenHydrology/flood-data/archive/master.zip"
        }

    **Response**:

    .. code-block:: http

        HTTP/1.0 202 ACCEPTED
        Content-Type: application/json
        Content-Length: 3
        Server: Werkzeug/0.10.4 Python/3.4.3
        Date: Thu, 05 Nov 2015 17:45:04 GMT
