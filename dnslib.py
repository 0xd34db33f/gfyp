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

#Note: this was originally code from dnstwist (https://github.com/elceef/dnstwist). I've since moved it out to an unmodified form that is accompanying this code.
#See dnstwist.py

from dnstwist import DomainFuzz
try:
	import dns.resolver
	module_dnspython = True
except:
	module_dnspython = False
	pass
try:
	import whois
	module_whois = True
except:
	module_whois = False
	pass

class dnslib:		
	
	def __init__(self):
		#Putting this here for now as a placeholder for the dynamic fuzzing code I'm working on.
		self.domains = []

	def checkDomain(self,dnsEntryName):
		fuzzer = DomainFuzz(dnsEntryName.lower())
		fuzzer.generate()
		domains = fuzzer.domains
	
		total_hits = 0
	
		for i in range(0, len(domains)):
			if module_dnspython:
				resolv = dns.resolver.Resolver()
				resolv.lifetime = 1
				resolv.timeout = 1
	
				try:
					ns = resolv.query(domains[i]['domain-name'], 'NS')
					domains[i]['ns'] = str(ns[0])[:-1].lower()
				except:
					pass
	
				if 'ns' in domains[i]:
					try:
						ns = resolv.query(domains[i]['domain-name'], 'A')
						domains[i]['a'] = str(ns[0])
					except:
						pass
		
					try:
						ns = resolv.query(domains[i]['domain-name'], 'AAAA')
						domains[i]['aaaa'] = str(ns[0])
					except:
						pass
	
					try:
						mx = resolv.query(domains[i]['domain-name'], 'MX')
						domains[i]['mx'] = str(mx[0].exchange)[:-1].lower()
					except:
						pass
	
			if 'ns' in domains[i] or 'a' in domains[i]:
				try:
					whoisdb = whois.query(domains[i]['domain-name'])
					domains[i]['created'] = str(whoisdb.creation_date).replace(' ', 'T')
					domains[i]['updated'] = str(whoisdb.last_updated).replace(' ', 'T')
				except:
					pass
		
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
				returnDomains.append([i['domain-name'],info])	
	
		return returnDomains
