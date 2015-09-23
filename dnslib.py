#!/usr/bin/env python
#
# dnstwist
#
# Generate and resolve domain variations to detect typo squatting,
# phishing and corporate espionage.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Marcin Ulikowski'
__version__ = '20150910'
__email__ = 'marcin@ulikowski.pl'

import re
import sys
import socket
import signal
import argparse
try:
	import dns.resolver
	module_dnspython = True
except:
	module_dnspython = False
	pass
try:
	import GeoIP
	module_geoip = True
except:
	module_geoip = False
	pass
try:
	import whois
	module_whois = True
except:
	module_whois = False
	pass

class dnslib:		
	# Internationalized domains not supported
	def validate_domain(self,domain):
		if len(domain) > 255:
			return False
		if domain[-1] == '.':
			domain = domain[:-1]
		allowed = re.compile('\A([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}\Z', re.IGNORECASE)
		return allowed.match(domain)
	
	def bitsquatting(self,domain):
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
		masks = [1, 2, 4, 8, 16, 32, 64, 128]
	
		for i in range(0, len(dom)):
			c = dom[i]
			for j in range(0, len(masks)):
				b = chr(ord(c) ^ masks[j])
				o = ord(b)
				if (o >= 48 and o <= 57) or (o >= 97 and o <= 122) or o == 45:
					out.append(dom[:i] + b + dom[i+1:] + '.' + tld)
	
		return out

	def flipit(self,substring):
        	glyphs = {
        	'd':['b', 'cl'], 'm':['n', 'rn'], 'l':['1', 'i'], 'o':['0'],
        	'w':['vv'], 'n':['m'], 'b':['d'], 'i':['l'], 'g':['q'], 'q':['g']
        	}
        	out = []
        	#Base case
        	currChar = substring[0]
        	if len(substring) == 1:
                	out = list(currChar)
                	if substring[0] in glyphs:
                        	for g in range(0,len(glyphs[currChar])):
                                	out.append(glyphs[currChar][g])
        	else:
                	sublist = self.flipit(substring[1:])
                	for sublistitem in sublist:
                        	out.append(currChar+sublistitem)
                	if substring[0] in glyphs:
                        	for g in range(0,len(glyphs[currChar])):
                                	for sublistitem in sublist:
                                        	out.append(glyphs[currChar][g]+sublistitem)
        	return out
	
	def homoglyph(self,domain):
		glyphs = {
		'd':['b', 'cl'], 'm':['n', 'nn', 'rn'], 'l':['1', 'i'], 'o':['0'],
		'w':['vv'], 'n':['m'], 'b':['d'], 'i':['1', 'l'], 'g':['q'], 'q':['g']
		}
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
		#Need to review this, based on the latest tickets for dnstwist this is busted so I'll sub it out for now with a less efficient algorithm.	
		#for ws in range(0, len(dom)):
		#	for i in range(0, (len(dom)-ws)+1):
		#		win = dom[i:i+ws]
	
		#		j = 0
		#		while j < ws:
		#			c = win[j]
		#			if c in glyphs:
		#				for g in range(0, len(glyphs[c])):
		#					win = win[:j] + glyphs[c][g] + win[j+1:]
	
		#					if len(glyphs[c][g]) > 1:
		#						j += len(glyphs[c][g]) - 1
		#					out.append(dom[:i] + win + dom[i+ws:] + '.' + tld)
	
		#			j += 1
		currList = self.flipit(dom)
        	for listItem in currList:
                	out.append(listItem + "."+tld)
		return list(set(out))
	
	def repetition(self,domain):
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
	
		for i in range(0, len(dom)):
			if dom[i].isalpha():
				out.append(dom[:i] + dom[i] + dom[i] + dom[i+1:] + '.' + tld)
	
		return out
	
	def transposition(self,domain):
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
	
		for i in range(0, len(dom)-1):
			if dom[i+1] != dom[i]:
				out.append(dom[:i] + dom[i+1] + dom[i] + dom[i+2:] + '.' + tld)
	
		return out
	
	def replacement(self,domain):
		keys = {
		'1':'2q', '2':'3wq1', '3':'4ew2', '4':'5re3', '5':'6tr4', '6':'7yt5', '7':'8uy6', '8':'9iu7', '9':'0oi8', '0':'po9',
		'q':'12wa', 'w':'3esaq2', 'e':'4rdsw3', 'r':'5tfde4', 't':'6ygfr5', 'y':'7uhgt6', 'u':'8ijhy7', 'i':'9okju8', 'o':'0plki9', 'p':'lo0',
		'a':'qwsz', 's':'edxzaw', 'd':'rfcxse', 'f':'tgvcdr', 'g':'yhbvft', 'h':'ujnbgy', 'j':'ikmnhu', 'k':'olmji', 'l':'kop',
		'z':'asx', 'x':'zsdc', 'c':'xdfv', 'v':'cfgb', 'b':'vghn', 'n':'bhjm', 'm':'njk'
		}
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
	
		for i in range(0, len(dom)):
			if dom[i] in keys:
				for c in range(0, len(keys[dom[i]])):
					out.append(dom[:i] + keys[dom[i]][c] + dom[i+1:] + '.' + tld)
	
		return out
	
	def omission(self,domain):
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
	
		for i in range(0, len(dom)):
			out.append(dom[:i] + dom[i+1:] + '.' + tld)
	
		return out
	
	def hyphenation(self,domain):
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
	
		for i in range(1, len(dom)):
			if dom[i] not in ['-', '.'] and dom[i-1] not in ['-', '.']:
				out.append(dom[:i] + '-' + dom[i:] + '.' + tld)
	
		return out
	
	def subdomain(self,domain):
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
	
		for i in range(1, len(dom)):
			if dom[i] not in ['-', '.'] and dom[i-1] not in ['-', '.']:
				out.append(dom[:i] + '.' + dom[i:] + '.' + tld)
	
		return out
	
	def insertion(self,domain):
		keys = {
		'1':'2q', '2':'3wq1', '3':'4ew2', '4':'5re3', '5':'6tr4', '6':'7yt5', '7':'8uy6', '8':'9iu7', '9':'0oi8', '0':'po9',
		'q':'12wa', 'w':'3esaq2', 'e':'4rdsw3', 'r':'5tfde4', 't':'6ygfr5', 'y':'7uhgt6', 'u':'8ijhy7', 'i':'9okju8', 'o':'0plki9', 'p':'lo0',
		'a':'qwsz', 's':'edxzaw', 'd':'rfcxse', 'f':'tgvcdr', 'g':'yhbvft', 'h':'ujnbgy', 'j':'ikmnhu', 'k':'olmji', 'l':'kop',
		'z':'asx', 'x':'zsdc', 'c':'xdfv', 'v':'cfgb', 'b':'vghn', 'n':'bhjm', 'm':'njk'
		}
		out = []
		dom = domain.rsplit('.', 1)[0]
		tld = domain.rsplit('.', 1)[1]
	
		for i in range(1, len(dom)-1):
			if dom[i] in keys:
				for c in range(0, len(keys[dom[i]])):
					out.append(dom[:i] + keys[dom[i]][c] + dom[i] + dom[i+1:] + '.' + tld)
					out.append(dom[:i] + dom[i] + keys[dom[i]][c] + dom[i+1:] + '.' + tld)
	
		return out
	
	def fuzz_domain(self,domain):
		domains = []
	
		for i in self.bitsquatting(domain):
			domains.append({ 'type':'Bitsquatting', 'domain':i })
		for i in self.homoglyph(domain):
			domains.append({ 'type':'Homoglyph', 'domain':i })
		for i in self.repetition(domain):
			domains.append({ 'type':'Repetition', 'domain':i })
		for i in self.transposition(domain):
			domains.append({ 'type':'Transposition', 'domain':i })
		for i in self.replacement(domain):
			domains.append({ 'type':'Replacement', 'domain':i })
		for i in self.omission(domain):
			domains.append({ 'type':'Omission', 'domain':i })
		for i in self.hyphenation(domain):
			domains.append({ 'type':'Hyphenation', 'domain':i })
		for i in self.insertion(domain):
			domains.append({ 'type':'Insertion', 'domain':i })
		for i in self.subdomain(domain):
			domains.append({ 'type':'Subdomain', 'domain':i })
	
		domains[:] = [x for x in domains if self.validate_domain(x['domain'])]
	
		return domains
	
	def checkDomain(self,dnsEntryName):
		domains = self.fuzz_domain(dnsEntryName.lower())
	
		total_hits = 0
	
		for i in range(0, len(domains)):
			if module_dnspython:
				resolv = dns.resolver.Resolver()
				resolv.lifetime = 1
				resolv.timeout = 1
	
				try:
					ns = resolv.query(domains[i]['domain'], 'NS')
					domains[i]['ns'] = str(ns[0])[:-1].lower()
				except:
					pass
	
				if 'ns' in domains[i]:
					try:
						ns = resolv.query(domains[i]['domain'], 'A')
						domains[i]['a'] = str(ns[0])
					except:
						pass
		
					try:
						ns = resolv.query(domains[i]['domain'], 'AAAA')
						domains[i]['aaaa'] = str(ns[0])
					except:
						pass
	
					try:
						mx = resolv.query(domains[i]['domain'], 'MX')
						domains[i]['mx'] = str(mx[0].exchange)[:-1].lower()
					except:
						pass
	
			if 'ns' in domains[i] or 'a' in domains[i]:
				try:
					whoisdb = whois.query(domains[i]['domain'])
					domains[i]['created'] = str(whoisdb.creation_date).replace(' ', 'T')
					domains[i]['updated'] = str(whoisdb.last_updated).replace(' ', 'T')
				except:
					pass
	
			#if 'a' in domains[i] or 'ns' in domains[i]:
			#	sys.stdout.write('!')
			#	sys.stdout.flush()
			#	total_hits += 1
			#else:
			#	sys.stdout.write('.')
			#	sys.stdout.flush()
	
		#sys.stdout.write(' %d hit(s)\n\n' % total_hits)
	
		returnDomains = []
		for i in domains:
			info = ''
	
			if 'a' in i:
				info += i['a']
				if 'country' in i:
					info += '/' + i['country']
				if 'banner-http' in i:
					info += ' HTTP:"%s"' % i['banner-http']
			elif 'ns' in i:
				info += 'NS:' + i['ns']
	
			if 'aaaa' in i:
				info += ' ' + i['aaaa']
	
			if 'mx' in i:
				info += ' MX:' + i['mx']
				if 'banner-smtp' in i:
					info += ' SMTP:"%s"' % i['banner-smtp']
	
			if 'created' in i and 'updated' in i and i['created'] == i['updated']:
				info += ' Created/Updated:' + i['created']
			else:
				if 'created' in i:
					info += ' Created:' + i['created']
				if 'updated' in i:
					info += ' Updated:' + i['updated']
	
			if info:
				returnDomains.append([i['domain'],info])	
				#sys.stdout.write('%-15s %-15s %s\n' % (i['type'], i['domain'], info))
				#sys.stdout.flush()
	
		return returnDomains
