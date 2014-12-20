#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, urllib2
from urllib import urlencode
import json, re, time, cookielib
sys.path.append("/home/filbertkm/bots/cleanupspam")
from RequestHandler import RequestHandler

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
	if 'descriptions' in entity:
		return entity['descriptions']
	else:
		return False

def getRC(reqHandler):
	params = {
		'action' : 'query',
		'list' : 'recentchanges',
		'rcnamespace' : 0,
		'rctype' : 'new',
		'rcshow' : 'anon',
		'rclimit' : 25,
		'rcprop' : 'title',
	}
	changes = reqHandler.get(params)

	pages = []
	for change in changes['query']['recentchanges']:
		entity = getEntity(reqHandler, change['title'])
		descriptions = getDescriptions(entity)
		if descriptions:
			if 'en' in descriptions:
				urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', descriptions['en']['value'])
				if urls:
					print "listing %s for deletion" % change['title']
					pages.append(change['title'])
				else:
					print "skipping %s" % change['title']
		else:
			print "no description for %s" % change['title']

	print "returning list of pages for processing"
	return pages

def checkIP():
# http://www.stopforumspam.com/search?q=199.180.117.224&export=json
	return true

def deletePages(reqHandler, pages):
	tokens = reqHandler.getTokens()
	params = {
		'action' : 'delete',
		'reason' : 'spam',
		'token' : tokens['deletetoken']
	}
	print pages

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
	print "%d pages for deletion" % len(pages)
	deletePages(rh, pages)

	print 'done'

if __name__ == "__main__":
	main()
