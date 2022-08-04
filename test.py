#!/usr/bin/env python3.5

import json
import re
import subprocess
import unittest
from urllib.request import Request, urlopen

html_data = '''
<!DOCTYPE html>
<html>
<head>
    <title>Test File</title>    
</head>
<body>
    <h1>Hello World</h1>
    <input id="interactive-text-1" style="width:6rem; height:1.5rem; " alt="Test Text" />    
</body>
</html>
'''


def request_factory(path='/'):
    url = 'http://127.0.0.1:5001%s' % path
    headers = {
        'Content-Type': 'application/html'
    }
    return Request(url, data=html_data.encode('utf-8'), headers=headers, method='POST')


class TestPdf(unittest.TestCase):

    def setUp(self):
        request = request_factory('/pdf?filename=sample.pdf')
        self.response = urlopen(request)

    def tearDown(self):
        self.response.close()

    def test_response_code(self):
        self.assertEqual(self.response.getcode(), 200)

    def test_headers(self):
        headers = dict(self.response.info())
        self.assertEqual(headers['Content-Type'], 'application/pdf')
        self.assertEqual(headers['Content-Disposition'], 'inline;filename=sample.pdf')

    def test_body(self):
        self.assertEqual(self.response.read()[:4], b'%PDF')


class TestPng(unittest.TestCase):

    def setUp(self):
        request = request_factory('/png?filename=sample.png')
        self.response = urlopen(request)

    def tearDown(self):
        self.response.close()

    def test_response_code(self):
        self.assertEqual(self.response.getcode(), 200)

    def test_headers(self):
        headers = dict(self.response.info())
        self.assertEqual(headers['Content-Type'], 'image/png')
        self.assertEqual(headers['Content-Disposition'], 'inline;filename=sample.png')

    def test_body(self):
        self.assertEqual(self.response.read()[:4], b'\x89PNG')


class TestMultiple(unittest.TestCase):

    def setUp(self):
        url = 'http://127.0.0.1:5001/multiple?filename=sample.pdf'
        headers = {
            'Content-Type': 'application/json'
        }
        data = json.dumps([html_data, html_data]).encode('utf-8')
        request = Request(url, data=data, headers=headers, method='POST')
        self.response = urlopen(request)

    def tearDown(self):
        self.response.close()

    def test_response_code(self):
        self.assertEqual(self.response.getcode(), 200)

    def test_headers(self):
        headers = dict(self.response.info())
        self.assertEqual(headers['Content-Type'], 'application/pdf')
        self.assertEqual(headers['Content-Disposition'], 'inline;filename=sample.pdf')

    def test_body(self):
        data = self.response.read()
        pages = re.findall(rb'<<\s+/Type\s+/Page\b', data, re.MULTILINE|re.DOTALL)
        self.assertEqual(len(pages), 2)


if __name__ == '__main__':
    unittest.main()
