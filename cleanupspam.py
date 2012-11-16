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

def getEntity(reqHandler, id):
	prefixedId = id.lower()
	params = {
		'action' : 'wbgetentities',
		'ids' : prefixedId,
		'format' : 'json'
	}
	entity = reqHandler.get(params)
	return entity['entities'][prefixedId]

def getDescriptions(entity):
	return entity['descriptions']

def getRC(reqHandler):
	params = {
		'action' : 'query',
		'list' : 'recentchanges',
		'rcnamespace' : 0,
		'rctype' : 'new',
		'rcshow' : 'anon',
		'rclimit' : 500,
		'rcprop' : 'title',
	}
	changes = reqHandler.get(params)

	pages = []
	for change in changes['query']['recentchanges']:
		entity = getEntity(reqHandler, change['title'])
		descriptions = getDescriptions(entity)
		if descriptions is not None:
			if 'en' in descriptions:
				urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', descriptions['en']['value'])
				if urls is not None:
					pages.append(change['title'])

	return pages

def deletePages(reqHandler, pages):
	tokens = reqHandler.getTokens()
	params = {
		'action' : 'delete',
		'reason' : 'spam',
		'token' : tokens['deletetoken']
	}

	for page in pages:
		params['title'] = page
		print 'deleting %s' % page
		reqHandler.post(params)
		time.sleep(2)

def main(*args):
	config = {
		'api' : 'http://wikidata-test-repo.wikimedia.de/w/api.php' ,
		'user' : '',
		'password' : ''
	}
	rh = RequestHandler(config)
	pages = getRC(rh)
	deletePages(rh, pages)

	print 'done'

if __name__ == "__main__":
	main()
