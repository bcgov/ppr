import sys
from http import HTTPStatus
from logging import getLogger

from simple_cloudevent import SimpleCloudEvent


def doc_service_callback(ce: SimpleCloudEvent):

    print(f'ce id: {ce.id}', file=sys.stdout)
    print(f'ce data: {ce.data}', file=sys.stdout)

    # if everything works return a 200
    # anything else will put the ce back on the queue to be re-attempted.
    return HTTPStatus.OK
