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


class PDFreactor:
    @property
    def apiKey(self):
        return self.__apiKey

    @apiKey.setter
    def apiKey(self, apiKey):
        self.__apiKey = apiKey
    url = ""

    def __init__(self, url="http://localhost:9423/service/rest"):
        """Constructor"""
        self.url = url
        if url is None:
            self.url = "http://localhost:9423/service/rest"
        if self.url.endswith('/'):
            self.url = self.url[:-1]
        self.__apiKey = None

    def convert(self, config, connectionSettings=None):
        if config is not None:
            config['clientName'] = "PYTHON"
            config['clientVersion'] = PDFreactor.VERSION

        url = self.url + "/convert.json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            options = json.dumps(config)
            req = Request(url, _encoded(options), headers)
            response = urlopen(req)
            result = response.read().decode('utf-8')
        except HTTPError as e:
            result = json.loads(e.read().decode('utf-8'))
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 422:
                raise self._createServerException(errorId, result['error'], result)
            elif e.code == 400:
                raise self._createServerException(errorId, 'Invalid client data. ' + result['error'], result)
            elif e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + result['error'], result)
            elif e.code == 413:
                raise self._createServerException(errorId, 'The configuration is too large to process.', result)
            elif e.code == 500:
                raise self._createServerException(errorId, result['error'], result)
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.', result)
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').', result)
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')
        return json.loads(result)

    def convertAsBinary(self, config, stream=None, connectionSettings=None):
        if config is not None:
            config['clientName'] = "PYTHON"
            config['clientVersion'] = PDFreactor.VERSION

        url = self.url + "/convert.bin"
        if isinstance(stream, dict):
            connectionSettings = stream
            stream = None
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            options = json.dumps(config)
            req = Request(url, _encoded(options), headers)
            response = urlopen(req)
            if stream:
                CHUNK = 2 * 1024
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    stream.write(chunk)
                stream.close()
                result = None
            else:
                result = response.read()
        except HTTPError as e:
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 422:
                raise self._createServerException(errorId, e.read().decode('utf-8'))
            elif e.code == 400:
                raise self._createServerException(errorId, 'Invalid client data. ' + e.read().decode('utf-8'))
            elif e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + e.read().decode('utf-8'))
            elif e.code == 413:
                raise self._createServerException(errorId, 'The configuration is too large to process.')
            elif e.code == 500:
                raise self._createServerException(errorId, e.read().decode('utf-8'))
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.')
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').')
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')
        return result

    def convertAsync(self, config, connectionSettings=None):
        if config is not None:
            config['clientName'] = "PYTHON"
            config['clientVersion'] = PDFreactor.VERSION

        url = self.url + "/convert/async.json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            options = json.dumps(config)
            req = Request(url, _encoded(options), headers)
            response = urlopen(req)
            result = response.read().decode('utf-8')
        except HTTPError as e:
            result = json.loads(e.read().decode('utf-8'))
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 422:
                raise self._createServerException(errorId, result['error'], result)
            elif e.code == 400:
                raise self._createServerException(errorId, 'Invalid client data. ' + result['error'], result)
            elif e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + result['error'], result)
            elif e.code == 413:
                raise self._createServerException(errorId, 'The configuration is too large to process.', result)
            elif e.code == 500:
                raise self._createServerException(errorId, result['error'], result)
            elif e.code == 503:
                raise self._createServerException(errorId, 'Asynchronous conversions are unavailable.', result)
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').', result)
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')
        documentId = None
        if response is not None and response.info() is not None:
            location = response.info().get("Location")
            if location is not None:
                documentId = location[location.rfind("/") + 1:len(location)]
            cookieHeader = response.info().get("Set-Cookie")
            if cookieHeader is not None and connectionSettings is not None:
                if 'cookies' not in connectionSettings:
                    connectionSettings['cookies'] = {}
                cookiesObj = SimpleCookie()
                cookiesObj.load(cookieHeader)
                for name in cookiesObj:
                    connectionSettings['cookies'][name] = cookiesObj[name].value
        return documentId

    def getProgress(self, documentId, connectionSettings=None):
        url = self.url + "/progress/" + documentId + ".json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            req = Request(url, None, headers)
            response = urlopen(req)
            req.get_method = lambda: "get"
            result = response.read().decode('utf-8')
        except HTTPError as e:
            result = json.loads(e.read().decode('utf-8'))
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 422:
                raise self._createServerException(errorId, result['error'], result)
            elif e.code == 404:
                raise self._createServerException(errorId, 'Document with the given ID was not found. ' + result['error'], result)
            elif e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + result['error'], result)
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.', result)
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').', result)
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')
        return json.loads(result)

    def getDocument(self, documentId, connectionSettings=None):
        url = self.url + "/document/" + documentId + ".json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            req = Request(url, None, headers)
            response = urlopen(req)
            req.get_method = lambda: "get"
            result = response.read().decode('utf-8')
        except HTTPError as e:
            result = json.loads(e.read().decode('utf-8'))
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 422:
                raise self._createServerException(errorId, result['error'], result)
            elif e.code == 404:
                raise self._createServerException(errorId, 'Document with the given ID was not found. ' + result['error'], result)
            elif e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + result['error'], result)
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.', result)
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').', result)
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')
        return json.loads(result)

    def getDocumentAsBinary(self, documentId, stream=None, connectionSettings=None):
        url = self.url + "/document/" + documentId + ".bin"
        if isinstance(stream, dict):
            connectionSettings = stream
            stream = None
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            req = Request(url, None, headers)
            response = urlopen(req)
            req.get_method = lambda: "get"
            if stream:
                CHUNK = 2 * 1024
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    stream.write(chunk)
                stream.close()
                result = None
            else:
                result = response.read()
        except HTTPError as e:
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 422:
                raise self._createServerException(errorId, e.read().decode('utf-8'))
            elif e.code == 404:
                raise self._createServerException(errorId, 'Document with the given ID was not found. ' + e.read().decode('utf-8'))
            elif e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + e.read().decode('utf-8'))
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.')
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').')
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')
        return result

    def getDocumentMetadata(self, documentId, connectionSettings=None):
        url = self.url + "/document/metadata/" + documentId + ".json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            req = Request(url, None, headers)
            response = urlopen(req)
            req.get_method = lambda: "get"
            result = response.read().decode('utf-8')
        except HTTPError as e:
            result = json.loads(e.read().decode('utf-8'))
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 422:
                raise self._createServerException(errorId, result['error'], result)
            elif e.code == 404:
                raise self._createServerException(errorId, 'Document with the given ID was not found. ' + result['error'], result)
            elif e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + result['error'], result)
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.', result)
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').', result)
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')
        return json.loads(result)

    def deleteDocument(self, documentId, connectionSettings=None):
        url = self.url + "/document/" + documentId + ".json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            req = Request(url, None, headers)
            response = urlopen(req)
            req.get_method = lambda: "delete"
            result = response.read().decode('utf-8')
        except HTTPError as e:
            result = json.loads(e.read().decode('utf-8'))
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 404:
                raise self._createServerException(errorId, 'Document with the given ID was not found. ' + result['error'], result)
            elif e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + result['error'], result)
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.', result)
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').', result)
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')

    def getVersion(self, connectionSettings=None):
        url = self.url + "/version.json"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            req = Request(url, None, headers)
            response = urlopen(req)
            req.get_method = lambda: "get"
            result = response.read().decode('utf-8')
        except HTTPError as e:
            result = json.loads(e.read().decode('utf-8'))
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + result['error'], result)
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.', result)
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').', result)
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')
        return json.loads(result)

    def getStatus(self, connectionSettings=None):
        url = self.url + "/status"
        if self.apiKey != None:
            url += '?apiKey=' + self.apiKey
        result = ""
        if (connectionSettings is not None and 'headers' in connectionSettings and len(connectionSettings['headers'].keys()) == False):
            headers = connectionSettings['headers']
        else:
            headers = {}
            if connectionSettings is not None and 'headers' in connectionSettings:
                for (key, value) in connectionSettings['headers'].items():
                    lcKey = key.lower()
                    if lcKey != "content-type" and lcKey != "range" and lcKey != "user-agent":
                        headers[key] = value
        headers['Content-Type'] = 'application/json'
        if connectionSettings is not None and 'cookies' in connectionSettings:
            headers['Cookie'] = '; '.join(['%s=%s' % (key, value) for (key, value) in connectionSettings['cookies'].items()])
        headers['User-Agent'] = 'PDFreactor Python API v8'
        headers['X-RO-User-Agent'] = 'PDFreactor Python API v8'
        req = None
        try:
            req = Request(url, None, headers)
            response = urlopen(req)
            req.get_method = lambda: "get"
            result = response.read().decode('utf-8')
        except HTTPError as e:
            result = json.loads(e.read().decode('utf-8'))
            errorId = ''
            if hasattr(e, 'headers'):
                errorId = e.headers['X-RO-Error-ID']
            if e.code == 401:
                raise self._createServerException(errorId, 'Unauthorized. ' + result['error'], result)
            elif e.code == 503:
                raise self._createServerException(errorId, 'PDFreactor Web Service is unavailable.', result)
            elif e.code > 400:
                raise self._createServerException(errorId, 'PDFreactor Web Service error (status: ' + str(e.code) + ').', result)
        except Exception as e:
            msg = e
            if hasattr(e, 'reason'):
                msg = e.reason
            raise UnreachableServiceException('Error connecting to PDFreactor Web Service at ' + self.url + '. Please make sure the PDFreactor Web Service is installed and running (Error: ' + str(msg) + ')')

    def getDocumentUrl(self, documentId):
        return self.url + "/document/" + documentId

    def getProgressUrl(self, documentId):
        return self.url + "/progress/" + documentId
    VERSION = 8

    def _createServerException(self, errorId=None, message=None, result=None):
        if errorId == 'server':
            return ServerException(errorId, message, result)
        elif errorId == 'asyncUnavailable':
            return AsyncUnavailableException(errorId, message, result)
        elif errorId == 'badRequest':
            return BadRequestException(errorId, message, result)
        elif errorId == 'commandRejected':
            return CommandRejectedException(errorId, message, result)
        elif errorId == 'conversionAborted':
            return ConversionAbortedException(errorId, message, result)
        elif errorId == 'conversionFailure':
            return ConversionFailureException(errorId, message, result)
        elif errorId == 'documentNotFound':
            return DocumentNotFoundException(errorId, message, result)
        elif errorId == 'resourceNotFound':
            return ResourceNotFoundException(errorId, message, result)
        elif errorId == 'invalidClient':
            return InvalidClientException(errorId, message, result)
        elif errorId == 'invalidConfiguration':
            return InvalidConfigurationException(errorId, message, result)
        elif errorId == 'noConfiguration':
            return NoConfigurationException(errorId, message, result)
        elif errorId == 'noInputDocument':
            return NoInputDocumentException(errorId, message, result)
        elif errorId == 'requestRejected':
            return RequestRejectedException(errorId, message, result)
        elif errorId == 'serviceUnavailable':
            return ServiceUnavailableException(errorId, message, result)
        elif errorId == 'unauthorized':
            return UnauthorizedException(errorId, message, result)
        elif errorId == 'unprocessableConfiguration':
            return UnprocessableConfigurationException(errorId, message, result)
        elif errorId == 'unprocessableInput':
            return UnprocessableInputException(errorId, message, result)
        elif errorId == 'notAcceptable':
            return NotAcceptableException(errorId, message, result)
        else:
            return ServerException(errorId, message, result)

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


class PDFreactorWebserviceException(Exception):
    def __init__(self, message):
        super(PDFreactorWebserviceException, self).__init__(message or "Unknown PDFreactor Web Service error")


class ServerException(PDFreactorWebserviceException):
    def __init__(self, errorId, message, result=None):
        super(ServerException, self).__init__(message)
        self.errorId = errorId
        self.result = result


class ClientException(PDFreactorWebserviceException):
    def __init__(self, message):
        super(ClientException, self).__init__(message)


class AsyncUnavailableException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(AsyncUnavailableException, self).__init__(errorId, message, result)


class BadRequestException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(BadRequestException, self).__init__(errorId, message, result)


class CommandRejectedException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(CommandRejectedException, self).__init__(errorId, message, result)


class ConversionAbortedException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(ConversionAbortedException, self).__init__(errorId, message, result)


class ConversionFailureException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(ConversionFailureException, self).__init__(errorId, message, result)


class DocumentNotFoundException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(DocumentNotFoundException, self).__init__(errorId, message, result)


class ResourceNotFoundException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(ResourceNotFoundException, self).__init__(errorId, message, result)


class InvalidClientException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(InvalidClientException, self).__init__(errorId, message, result)


class InvalidConfigurationException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(InvalidConfigurationException, self).__init__(errorId, message, result)


class NoConfigurationException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(NoConfigurationException, self).__init__(errorId, message, result)


class NoInputDocumentException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(NoInputDocumentException, self).__init__(errorId, message, result)


class RequestRejectedException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(RequestRejectedException, self).__init__(errorId, message, result)


class ServiceUnavailableException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(ServiceUnavailableException, self).__init__(errorId, message, result)


class UnauthorizedException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(UnauthorizedException, self).__init__(errorId, message, result)


class UnprocessableConfigurationException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(UnprocessableConfigurationException, self).__init__(errorId, message, result)


class UnprocessableInputException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(UnprocessableInputException, self).__init__(errorId, message, result)


class NotAcceptableException(ServerException):
    def __init__(self, errorId, message, result=None):
        super(NotAcceptableException, self).__init__(errorId, message, result)


class UnreachableServiceException(ClientException):
    def __init__(self, message):
        super(UnreachableServiceException, self).__init__(message)


class InvalidServiceException(ClientException):
    def __init__(self, message):
        super(InvalidServiceException, self).__init__(message)
