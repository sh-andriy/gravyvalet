import logging

from django.http import HttpResponse

# from django.shortcuts import render

# Create your views here.


logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse(
        "Hello, world. Welcome to the continental, rated two stars on tripadvisor."
    )


def connect_box(request):
    logger.info('@@@ got request for connect_box')
    logger.info('@@@   request ib:({})'.format(request))
    return HttpResponse("You tried to box, but box we didn't.")
