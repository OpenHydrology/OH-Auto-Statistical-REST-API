OH Auto Statistical web API
===========================

Version |version|


.. _api/doc:

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
        Content-Length: 5
        Location: http://localhost:5000/api/v0/analysis-tasks/124cce24-b02f-4ad8-9475-e8826fb4e655
        Server: Werkzeug/0.10.4 Python/3.4.3
        Date: Thu, 05 Nov 2015 17:45:04 GMT

        null

.. http:post:: /api/v0/analyses/(task_id)
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


.. http:get:: /api/v0/analysis-tasks/(task_id)
    :synopsis: Returns the analysis status or redirects to the analysis report when completed

    If the analysis task is not yet completed the task's status is returned (json). Otherwise redirects to the analysis
    report itself.

    :param task_id: Task identifier

    :resheader Content-Type: :mimetype:`application/json`

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
        Content-Length: 0
        Location: http://localhost:5000/api/v0/analysis/124cce24-b02f-4ad8-9475-e8826fb4e655
        Server: Werkzeug/0.10.4 Python/3.4.3
        Date: Thu, 05 Nov 2015 20:06:26 GMT
