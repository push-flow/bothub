import logging

from rest_framework import status


logger = logging.getLogger('bothub.health.checks')

CHECK_ACCESSIBLE_API_URL = '/api/repositories/'


def check_database_connection(**kwargs):
    from django.db import connections
    from django.db.utils import OperationalError
    if len(connections.all()) is 0:
        return False
    logger.info('found {} database connection'.format(len(connections.all())))
    for i, conn in enumerate(connections.all(), 1):
        db_conn = connections['default']
        try:
            db_conn.cursor()
            logger.info('#{} db connection OKAY'.format(i))
        except OperationalError as e:
            logger.warning('#{} db connection ERROR'.format(i))
            return False
    return True


def check_accessible_api(request, **kwargs):
    from django.test import Client
    logger.info('making request to {}'.format(CHECK_ACCESSIBLE_API_URL))
    client = Client()
    response = client.get(CHECK_ACCESSIBLE_API_URL)
    logger.info('{} status code: {}'.format(
        CHECK_ACCESSIBLE_API_URL,
        response.status_code))
    if response.status_code is status.HTTP_200_OK:
        return True
    return False