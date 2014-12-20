#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
from urllib import urlencode
import json, re, time, cookielib

class RequestHandler:

	def __init__(self, config):
		self.config = config
		self._cj = cookielib.CookieJar()
		self._opener = urllib2.build_opener(
                urllib2.HTTPCookieProcessor(self._cj)
        )
		self._editToken = None
		self.login()

	def login(self):
		params = {
			'action' : 'login',
			'lgname' : self.config['user'],
			'lgpassword' : self.config['password']
		}

		result = self.post(params)

		if result['login']['result'] == 'Success':
			self._editToken = self.getToken()
			return True
		elif result['login']['result'] == 'NeedToken':
			params['lgtoken'] = result['login']['token']
			result = self.post(params)
			tokens = self.getTokens()
			self._editToken = tokens['edittoken']
			return True
		else:
			return False

	def get(self, params):
		params['format'] = 'json'
		url = urllib2.Request(self.config['api']+"?"+ urlencode(params))
		content = self._opener.open(url).read()
		return json.loads(content)

	def post(self, params):
		params['format'] = 'json'
		url = urllib2.Request(self.config['api'], urlencode(params))
		content = self._opener.open(url).read()
		return json.loads(content)

	def getTokens(self):
		params = {
			'action' : 'tokens',
			'type' : 'edit|delete'
		}
		js = self.post(params)
		return js['tokens']
