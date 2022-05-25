#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
from pdfreactor.api import *

from time import localtime, strftime, sleep

# The content to render
fileHandle = open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/contentPython.html')))
content = fileHandle.read()

# Create new PDFreactor instance
# pdfReactor = PDFreactor("http://yourServer:9423/service/rest")
pdfReactor = PDFreactor()

# Creates today's date
date = strftime("%m/%d/%Y %H:%M:%S %p", localtime())

# Get base URL path
path = os.getenv('REQUEST_URI')

# If the environment variable was not found
if not path:
    # try this one:
    path = os.environ['PATH_INFO']

# Create a new PDFreactor configuration object
config = {
    # Specify the input document
    'document': content,
    # Set a base URL for images, style sheets, links
    'baseURL': "http://" + os.getenv("HTTP_HOST") + path,
    # Set an appropriate log level
    'logLevel': PDFreactor.LogLevel.WARN,
    # Set the title of the created PDF
    'title': "Demonstration of the PDFreactor Python API",
    # Set the author of the created PDF
    'author': "Myself",
    # Enable links in the PDF document
    'addLinks': True,
    # Enable bookmarks in the PDF document
    'addBookmarks': True,
    # Set some viewer preferences
    'viewerPreferences': [
        PDFreactor.ViewerPreferences.FIT_WINDOW,
        PDFreactor.ViewerPreferences.PAGE_MODE_USE_THUMBS
    ],
    # Add user style sheets
    'userStyleSheets': [
        {
            'content': "@page {"
                           "@top-center {"
                               "content: 'PDFreactor Python API demonstration';"
                           "}"
                           "@bottom-center {"
                               "content: 'Created on " + date + "';"
                           "}"
                       "}"
        },
        {'uri': "../../resources/common.css"}
    ]
}

try:
    # Sync
    file1 = open("stream-sync.pdf", "w")
    pdfReactor.convertAsBinary(config, file1)
    file1.close()

    # Async
    documentId = pdfReactor.convertAsync(config)

    while True:
        sleep(0.5)
        progress = pdfReactor.getProgress(documentId)

        if progress['finished']:
            break

    file2 = open("stream-async.pdf", "w")
    pdfReactor.getDocumentAsBinary(documentId, file2)
    file2.close()

    print("Content-Type: text/html\n\n")
    print("<h1>2 files successfully written: 'stream-sync.pdf' and 'stream-async.pdf'. Please check your file system.</h1>")
except Exception as e:
    # Not successful, print error and log
    print("Content-type: text/html\n\n")
    print("<h1>An Error Has Occurred</h1>")
    print("<h2>" + str(e) + "</h2>")
