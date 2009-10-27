#!/usr/bin/env python

import httplib2
import urllib

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree

from saml2.samlp import NAMESPACE as SAMLP_NAMESPACE

NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"

class _Http(object):
    """ For writing to a HTTP server using POST """
    def __init__(self, path, keyfile=None, certfile=None):
        self.path = path
        self.server = httplib2.Http()
        if keyfile:
            self.server.add_certificate(keyfile, certfile, "")

    def write(self, data):
        (response, content) = self.server.request(self.path, "POST", data)
        if response.status == 200:
            return content
        else:
            return False

class SOAPClient(object):
    
    def __init__(self, server_url, keyfile=None, certfile=None):
        self.server = _Http(server_url, keyfile, certfile)
        
    def send(self, request):
        soap_message = self.make_soap_enveloped_saml_request(request)
        response = self.server.write(soap_message)
        if response:
            return self.parse_soap_enveloped_saml_response(response)

    def parse_soap_enveloped_saml_response(self, text):
        envelope = ElementTree.fromstring(text)
        assert envelope.tag == '{%s}Envelope' % NAMESPACE
        
        assert len(envelope) == 1
        body = envelope[0]
        assert body.tag == '{%s}Body' % NAMESPACE
        assert len(body) == 1
        saml_part = body[0]
        if saml_part.tag == '{%s}Response' % SAMLP_NAMESPACE:
            return ElementTree.tostring(saml_part, encoding="UTF-8")
        else:
            return ""
            
    def make_soap_enveloped_saml_request(self, request):
        """ Returns a soap envelope containing a SAML request
        as a text string.
        
        :param request: The SAML request
        :return: The SOAP envelope as a string
        """
        envelope = ElementTree.Element('')
        envelope.tag = '{%s}Envelope' % NAMESPACE

        body = ElementTree.Element('')
        body.tag = '{%s}Body' % NAMESPACE
        envelope.append(body)

        request.become_child_element(body)

        return ElementTree.tostring(envelope, encoding="UTF-8")