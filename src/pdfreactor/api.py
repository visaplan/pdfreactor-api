# RealObjects PDFreactor Python Client version 8
# https://www.pdfreactor.com
#
# Released under the following license:
#
# The MIT License (MIT)
#
# Copyright (c) 2015-2022 RealObjects GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Changes by Tobias Herp, visaplan GmbH:
# - moved the Python version switching to the top (out of the executed code)
# - comparison to None by identity rather than equality
# - options processing:
#   - _spiced_config method (to have always a config dict with client info)
#   - _spiced_headers method (code deduplication for headers and cookies)
#   - _sacs helper function for (stream, connectionSettings) options
# - class cleanup:
#   - removed the `url` class attribute; turned it in a property instead
#   - modified the apiKey property setter to store a quoted value; pre-quoted
#     values are used as they are.
# - exceptions:
#   - Moved all exception classes to a dedicated .exceptions module.
#   - Removed all classes which inherited from ServerException,
#   - which in turn now inherits from HTTPError;
#   - instead of computing the errorId beforehand (to choose an exception class),
#     we provide a read-only property of that name.
#   - Removed the now obsolete method PDFreactor._createServerException.
#   - New property ServerException.result
#   - New property ServerException.pdfreactor_error
#     (containing the 'error' value, if .result contains an JSON object,
#     or some fallback text which cites the first 200 characters of the textual
#     result)
#   - New property ServerException.pdfreactor_says
#     (after some strings used before when creating exceptions)
#   - UnreachableServiceException:
#     - Arguments are now (Exception, URL) instead of the message text;
#     - Instead of computing the message for creation, we do this work
#       when creating the string representation.
#     - Be sure not to wrap exceptions as UnreachableServiceException
#       which occur after the urlopen call (try ... except ... else)
# - other changes:
#   - instead of monkey-patching the get_method method, use {Get,Delete}Request
#     classes
#   - moved the (somewhat hidden) VERSION attribute up
#   - removed unnecessary assignments to result and req variables
#   - for missing subdicts (headers, cookies), use the dict.setdefault method

import json
import sys

if sys.version_info[0] == 2:
    from urllib2 import HTTPError
    from urllib2 import Request, urlopen
    from Cookie import SimpleCookie


    def _encoded(s):
        return s
else:
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
    from http.cookies import SimpleCookie


    def _encoded(s):
        # we reproduce the original behaviour here ...
        return s.encode()

from ._args import _sacs
from .exceptions import ServerException, UnreachableServiceException

__all__ = [
    'PDFreactor',  # the API object
    # exception classes (more in ./exceptions.py):
    'UnreachableServiceException',
    'ServerException',  # an HTTPError
    ]


class GetRequest(Request):
    def get_method(self):
        return 'get'


class DeleteRequest(Request):
    def get_method(self):
        return 'delete'


class PDFreactor:
    @property
    def apiKey(self):
        return self.__apiKey

    @apiKey.setter
    def apiKey(self, apiKey):
        self.__apiKey = apiKey

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, val):
        if val is None:
            val = "http://localhost:9423/service/rest"
        elif val.endswith('/'):
            val = val.rstrip('/')
        self.__url = val

    def __init__(self, url=None):
        """Constructor"""
        self.url = url  # the setter takes care of the default value
        self.__apiKey = None

    VERSION = 8

    def _spiced_config(self, config):
        if config is None:
            config = {}
        config.update({
            'clientName': "PYTHON",
            'clientVersion': PDFreactor.VERSION,
            })
        return config

    def _spiced_headers(self, connectionSettings):
        # In HTTP/1.x, header fields names are case-insensitive:
        # https://datatracker.ietf.org/doc/html/rfc7230#section-3.2 
        # In HTTP/2.0, they must be converted to lowercase:
        # https://www.rfc-editor.org/rfc/rfc7540#section-8.1.2
        if connectionSettings is None:
            connectionSettings = {}
        API_HEADERS = {
            'Content-Type':     'application/json',
            'User-Agent':       'PDFreactor Python API v8',
            'X-RO-User-Agent':  'PDFreactor Python API v8',
            }
        PRETTY_KEY = {key.lower(): key for key in API_HEADERS.keys()}
        missing = set(PRETTY_KEY)
        headers = connectionSettings.setdefault('headers', {})
        for key, val in headers.items():
            lkey = key.lower()
            if lkey in missing:
                headers[key] = API_HEADERS[PRETTY_KEY[lkey]]
                missing.remove(lkey)
        for lkey in missing:
            key = PRETTY_KEY[lkey]
            headers[key] = API_HEADERS[key]
        # NOTE: these cookies won't be sent back by the PDFreactor service to
        # your client; for this to happen (e.g to make exports of restricted
        # contents of your server), specify config['cookies']
        # (a list of {'key': ..., 'value': ...} dictionaries) 
        if 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join([
                    '%s=%s' % (key, value)
                    for (key, value) in connectionSettings['cookies'].items()
                    ])
        return headers

    def convert(self, config, connectionSettings=None):
        config = self._spiced_config(config)
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/convert.json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            options = json.dumps(config)
            req = Request(url, _encoded(options), headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            result = response.read().decode('utf-8')
            return json.loads(result)

    def convertAsBinary(self, config, *args, **kwargs):
        config = self._spiced_config(config)
        stream, connectionSettings = _sacs(*args, **kwargs)
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/convert.bin"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            options = json.dumps(config)
            req = Request(url, _encoded(options), headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            if stream:
                CHUNK = 2 * 1024
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    stream.write(chunk)
                stream.close()
                return None
            else:
                result = response.read()
                return result

    def convertAsync(self, config, connectionSettings=None):
        config = self._spiced_config(config)
        # w/o *given* connectionSettings, we lack a place to store cookies:
        have_cs = connectionSettings is not None
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/convert/async.json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            options = json.dumps(config)
            req = Request(url, _encoded(options), headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            result = response.read().decode('utf-8')

        documentId = None
        if response is not None and response.info() is not None:
            location = response.info().get("Location")
            if location is not None:
                documentId = location[location.rfind("/") + 1:len(location)]
            cookieHeader = response.info().get("Set-Cookie")
            if cookieHeader is not None and have_cs:
                cookies = connectionSettings.setdefault('cookies', {})
                cookiesObj = SimpleCookie()
                cookiesObj.load(cookieHeader)
                for name in cookiesObj:
                    cookies[name] = cookiesObj[name].value
        return documentId

    def getProgress(self, documentId, connectionSettings=None):
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/progress/" + documentId + ".json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            req = GetRequest(url, None, headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            result = response.read().decode('utf-8')
            return json.loads(result)

    def getDocument(self, documentId, connectionSettings=None):
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/document/" + documentId + ".json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            req = GetRequest(url, None, headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            result = response.read().decode('utf-8')
            return json.loads(result)

    def getDocumentAsBinary(self, documentId, *args, **kwargs):
        stream, connectionSettings = _sacs(*args, **kwargs)
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/document/" + documentId + ".bin"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            req = GetRequest(url, None, headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            if stream:
                CHUNK = 2 * 1024
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    stream.write(chunk)
                stream.close()
                return None
            else:
                result = response.read()
                return result

    def getDocumentMetadata(self, documentId, connectionSettings=None):
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/document/metadata/" + documentId + ".json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            req = GetRequest(url, None, headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            result = response.read().decode('utf-8')
            return json.loads(result)

    def deleteDocument(self, documentId, connectionSettings=None):
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/document/" + documentId + ".json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            req = DeleteRequest(url, None, headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            result = response.read().decode('utf-8')

    def getVersion(self, connectionSettings=None):
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/version.json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            req = GetRequest(url, None, headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            result = response.read().decode('utf-8')
            return json.loads(result)

    def getStatus(self, connectionSettings=None):
        headers = self._spiced_headers(connectionSettings)

        url = self.url + "/status"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        try:
            req = GetRequest(url, None, headers)
            response = urlopen(req)
        except HTTPError as e:
            raise ServerException(e)
        except Exception as e:
            raise UnreachableServiceException(e, url)
        else:
            result = response.read().decode('utf-8')

    def getDocumentUrl(self, documentId):
        return self.url + "/document/" + documentId

    def getProgressUrl(self, documentId):
        return self.url + "/progress/" + documentId

    class CallbackType:
        FINISH = "FINISH"
        PROGRESS = "PROGRESS"
        START = "START"

    class Cleanup:
        CYBERNEKO = "CYBERNEKO"
        JTIDY = "JTIDY"
        NONE = "NONE"
        TAGSOUP = "TAGSOUP"

    class ColorSpace:
        CMYK = "CMYK"
        RGB = "RGB"

    class Conformance:
        PDF = "PDF"
        PDFA1A = "PDFA1A"
        PDFA1A_PDFUA1 = "PDFA1A_PDFUA1"
        PDFA1B = "PDFA1B"
        PDFA2A = "PDFA2A"
        PDFA2A_PDFUA1 = "PDFA2A_PDFUA1"
        PDFA2B = "PDFA2B"
        PDFA2U = "PDFA2U"
        PDFA3A = "PDFA3A"
        PDFA3A_PDFUA1 = "PDFA3A_PDFUA1"
        PDFA3B = "PDFA3B"
        PDFA3U = "PDFA3U"
        PDFUA1 = "PDFUA1"
        PDFX1A_2001 = "PDFX1A_2001"
        PDFX1A_2003 = "PDFX1A_2003"
        PDFX3_2002 = "PDFX3_2002"
        PDFX3_2003 = "PDFX3_2003"
        PDFX4 = "PDFX4"
        PDFX4P = "PDFX4P"

    class ContentType:
        BINARY = "BINARY"
        BMP = "BMP"
        GIF = "GIF"
        HTML = "HTML"
        JPEG = "JPEG"
        JSON = "JSON"
        NONE = "NONE"
        PDF = "PDF"
        PNG = "PNG"
        TEXT = "TEXT"
        TIFF = "TIFF"
        XML = "XML"

    class CssPropertySupport:
        ALL = "ALL"
        HTML = "HTML"
        HTML_THIRD_PARTY = "HTML_THIRD_PARTY"
        HTML_THIRD_PARTY_LENIENT = "HTML_THIRD_PARTY_LENIENT"

    class Doctype:
        AUTODETECT = "AUTODETECT"
        HTML5 = "HTML5"
        XHTML = "XHTML"
        XML = "XML"

    class Encryption:
        NONE = "NONE"
        TYPE_128 = "TYPE_128"
        TYPE_40 = "TYPE_40"

    class ErrorPolicy:
        CONFORMANCE_VALIDATION_UNAVAILABLE = "CONFORMANCE_VALIDATION_UNAVAILABLE"
        LICENSE = "LICENSE"
        MISSING_RESOURCE = "MISSING_RESOURCE"
        UNCAUGHT_JAVASCRIPT_EXCEPTION = "UNCAUGHT_JAVASCRIPT_EXCEPTION"

    class ExceedingContentAgainst:
        NONE = "NONE"
        PAGE_BORDERS = "PAGE_BORDERS"
        PAGE_CONTENT = "PAGE_CONTENT"
        PARENT = "PARENT"

    class ExceedingContentAnalyze:
        CONTENT = "CONTENT"
        CONTENT_AND_BOXES = "CONTENT_AND_BOXES"
        CONTENT_AND_STATIC_BOXES = "CONTENT_AND_STATIC_BOXES"
        NONE = "NONE"

    class HttpsMode:
        LENIENT = "LENIENT"
        STRICT = "STRICT"

    class JavaScriptDebugMode:
        EXCEPTIONS = "EXCEPTIONS"
        FUNCTIONS = "FUNCTIONS"
        LINES = "LINES"
        NONE = "NONE"
        POSITIONS = "POSITIONS"

    class JavaScriptMode:
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"
        ENABLED_NO_LAYOUT = "ENABLED_NO_LAYOUT"
        ENABLED_REAL_TIME = "ENABLED_REAL_TIME"
        ENABLED_TIME_LAPSE = "ENABLED_TIME_LAPSE"

    class KeystoreType:
        JKS = "JKS"
        PKCS12 = "PKCS12"

    class LogLevel:
        DEBUG = "DEBUG"
        FATAL = "FATAL"
        INFO = "INFO"
        NONE = "NONE"
        PERFORMANCE = "PERFORMANCE"
        WARN = "WARN"

    class MediaFeature:
        ASPECT_RATIO = "ASPECT_RATIO"
        COLOR = "COLOR"
        COLOR_INDEX = "COLOR_INDEX"
        DEVICE_ASPECT_RATIO = "DEVICE_ASPECT_RATIO"
        DEVICE_HEIGHT = "DEVICE_HEIGHT"
        DEVICE_WIDTH = "DEVICE_WIDTH"
        GRID = "GRID"
        HEIGHT = "HEIGHT"
        MONOCHROME = "MONOCHROME"
        ORIENTATION = "ORIENTATION"
        RESOLUTION = "RESOLUTION"
        WIDTH = "WIDTH"

    class MergeMode:
        APPEND = "APPEND"
        ARRANGE = "ARRANGE"
        OVERLAY = "OVERLAY"
        OVERLAY_BELOW = "OVERLAY_BELOW"
        PREPEND = "PREPEND"

    class OutputIntentDefaultProfile:
        FOGRA39 = "Coated FOGRA39"
        GRACOL = "Coated GRACoL 2006"
        IFRA = "ISO News print 26% (IFRA)"
        JAPAN = "Japan Color 2001 Coated"
        JAPAN_NEWSPAPER = "Japan Color 2001 Newspaper"
        JAPAN_UNCOATED = "Japan Color 2001 Uncoated"
        JAPAN_WEB = "Japan Web Coated (Ad)"
        SWOP = "US Web Coated (SWOP) v2"
        SWOP_3 = "Web Coated SWOP 2006 Grade 3 Paper"

    class OutputType:
        BMP = "BMP"
        GIF = "GIF"
        GIF_DITHERED = "GIF_DITHERED"
        JPEG = "JPEG"
        PDF = "PDF"
        PNG = "PNG"
        PNG_AI = "PNG_AI"
        PNG_TRANSPARENT = "PNG_TRANSPARENT"
        PNG_TRANSPARENT_AI = "PNG_TRANSPARENT_AI"
        TIFF_CCITT_1D = "TIFF_CCITT_1D"
        TIFF_CCITT_1D_DITHERED = "TIFF_CCITT_1D_DITHERED"
        TIFF_CCITT_GROUP_3 = "TIFF_CCITT_GROUP_3"
        TIFF_CCITT_GROUP_3_DITHERED = "TIFF_CCITT_GROUP_3_DITHERED"
        TIFF_CCITT_GROUP_4 = "TIFF_CCITT_GROUP_4"
        TIFF_CCITT_GROUP_4_DITHERED = "TIFF_CCITT_GROUP_4_DITHERED"
        TIFF_LZW = "TIFF_LZW"
        TIFF_PACKBITS = "TIFF_PACKBITS"
        TIFF_UNCOMPRESSED = "TIFF_UNCOMPRESSED"

    class OverlayRepeat:
        ALL_PAGES = "ALL_PAGES"
        LAST_PAGE = "LAST_PAGE"
        NONE = "NONE"
        TRIM = "TRIM"

    class PageOrder:
        BOOKLET = "BOOKLET"
        BOOKLET_RTL = "BOOKLET_RTL"
        EVEN = "EVEN"
        ODD = "ODD"
        REVERSE = "REVERSE"

    class PagesPerSheetDirection:
        DOWN_LEFT = "DOWN_LEFT"
        DOWN_RIGHT = "DOWN_RIGHT"
        LEFT_DOWN = "LEFT_DOWN"
        LEFT_UP = "LEFT_UP"
        RIGHT_DOWN = "RIGHT_DOWN"
        RIGHT_UP = "RIGHT_UP"
        UP_LEFT = "UP_LEFT"
        UP_RIGHT = "UP_RIGHT"

    class PdfScriptTriggerEvent:
        AFTER_PRINT = "AFTER_PRINT"
        AFTER_SAVE = "AFTER_SAVE"
        BEFORE_PRINT = "BEFORE_PRINT"
        BEFORE_SAVE = "BEFORE_SAVE"
        CLOSE = "CLOSE"
        OPEN = "OPEN"

    class ProcessingPreferences:
        SAVE_MEMORY_IMAGES = "SAVE_MEMORY_IMAGES"

    class QuirksMode:
        DETECT = "DETECT"
        QUIRKS = "QUIRKS"
        STANDARDS = "STANDARDS"

    class ResolutionUnit:
        DPCM = "DPCM"
        DPI = "DPI"
        DPPX = "DPPX"
        TDPCM = "TDPCM"
        TDPI = "TDPI"
        TDPPX = "TDPPX"

    class ResourceType:
        ATTACHMENT = "ATTACHMENT"
        DOCUMENT = "DOCUMENT"
        FONT = "FONT"
        ICC_PROFILE = "ICC_PROFILE"
        IFRAME = "IFRAME"
        IMAGE = "IMAGE"
        LICENSEKEY = "LICENSEKEY"
        MERGE_DOCUMENT = "MERGE_DOCUMENT"
        OBJECT = "OBJECT"
        RUNNING_DOCUMENT = "RUNNING_DOCUMENT"
        SCRIPT = "SCRIPT"
        STYLESHEET = "STYLESHEET"
        UNKNOWN = "UNKNOWN"
        XHR = "XHR"

    class SigningMode:
        SELF_SIGNED = "SELF_SIGNED"
        VERISIGN_SIGNED = "VERISIGN_SIGNED"
        WINCER_SIGNED = "WINCER_SIGNED"

    class ViewerPreferences:
        CENTER_WINDOW = "CENTER_WINDOW"
        DIRECTION_L2R = "DIRECTION_L2R"
        DIRECTION_R2L = "DIRECTION_R2L"
        DISPLAY_DOC_TITLE = "DISPLAY_DOC_TITLE"
        DUPLEX_FLIP_LONG_EDGE = "DUPLEX_FLIP_LONG_EDGE"
        DUPLEX_FLIP_SHORT_EDGE = "DUPLEX_FLIP_SHORT_EDGE"
        DUPLEX_SIMPLEX = "DUPLEX_SIMPLEX"
        FIT_WINDOW = "FIT_WINDOW"
        HIDE_MENUBAR = "HIDE_MENUBAR"
        HIDE_TOOLBAR = "HIDE_TOOLBAR"
        HIDE_WINDOW_UI = "HIDE_WINDOW_UI"
        NON_FULLSCREEN_PAGE_MODE_USE_NONE = "NON_FULLSCREEN_PAGE_MODE_USE_NONE"
        NON_FULLSCREEN_PAGE_MODE_USE_OC = "NON_FULLSCREEN_PAGE_MODE_USE_OC"
        NON_FULLSCREEN_PAGE_MODE_USE_OUTLINES = "NON_FULLSCREEN_PAGE_MODE_USE_OUTLINES"
        NON_FULLSCREEN_PAGE_MODE_USE_THUMBS = "NON_FULLSCREEN_PAGE_MODE_USE_THUMBS"
        PAGE_LAYOUT_ONE_COLUMN = "PAGE_LAYOUT_ONE_COLUMN"
        PAGE_LAYOUT_SINGLE_PAGE = "PAGE_LAYOUT_SINGLE_PAGE"
        PAGE_LAYOUT_TWO_COLUMN_LEFT = "PAGE_LAYOUT_TWO_COLUMN_LEFT"
        PAGE_LAYOUT_TWO_COLUMN_RIGHT = "PAGE_LAYOUT_TWO_COLUMN_RIGHT"
        PAGE_LAYOUT_TWO_PAGE_LEFT = "PAGE_LAYOUT_TWO_PAGE_LEFT"
        PAGE_LAYOUT_TWO_PAGE_RIGHT = "PAGE_LAYOUT_TWO_PAGE_RIGHT"
        PAGE_MODE_FULLSCREEN = "PAGE_MODE_FULLSCREEN"
        PAGE_MODE_USE_ATTACHMENTS = "PAGE_MODE_USE_ATTACHMENTS"
        PAGE_MODE_USE_NONE = "PAGE_MODE_USE_NONE"
        PAGE_MODE_USE_OC = "PAGE_MODE_USE_OC"
        PAGE_MODE_USE_OUTLINES = "PAGE_MODE_USE_OUTLINES"
        PAGE_MODE_USE_THUMBS = "PAGE_MODE_USE_THUMBS"
        PICKTRAYBYPDFSIZE_FALSE = "PICKTRAYBYPDFSIZE_FALSE"
        PICKTRAYBYPDFSIZE_TRUE = "PICKTRAYBYPDFSIZE_TRUE"
        PRINTSCALING_APPDEFAULT = "PRINTSCALING_APPDEFAULT"
        PRINTSCALING_NONE = "PRINTSCALING_NONE"

    class XmpPriority:
        HIGH = "HIGH"
        LOW = "LOW"
        NONE = "NONE"
