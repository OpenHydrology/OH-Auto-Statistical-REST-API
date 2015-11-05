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
        Location: http://localhost:5000/api/v0/analyses_status/124cce24-b02f-4ad8-9475-e8826fb4e655
        Server: Werkzeug/0.10.4 Python/3.4.3
        Date: Thu, 05 Nov 2015 17:45:04 GMT

        null


.. http:get:: /api/v0/analyses_status/(task_id)
    :synopsis: Returns analysis status or the OH Auto Statistical report when completed

    If the analysis task is not yet completed the task's status is returned (json). Otherwise the analysis report itself
    is returned.

    :param task_id: Task identifier

    :resheader Content-Type: - :mimetype:`application/json`
                             - :mimetype:`text/plain; charset=utf-8`

    **Request**:

    .. code-block:: http

        GET api/v0/analyses_status/124cce24-b02f-4ad8-9475-e8826fb4e655 HTTP/1.0
        Accept: */*
        Host: localhost:5000

    **Response (task completed)**:

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
