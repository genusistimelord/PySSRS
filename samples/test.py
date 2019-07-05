#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from ssrs.SSRS import SSRS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

Service	  = 'http://servername/reportserver/ReportService2010.asmx?WSDL'
Execution = 'http://servername/reportserver/ReportExecution2005.asmx?WSDL'
user	  = 'username'
password  = 'password'
domain    = 'STRUCTURETEC'
RS		= SSRS(Service, Execution, user, password, domain)
RenderedReport =  None

try:
	Report = RS.RequestReport(path='/DMS Reports/BEP Executive Five-Year Plan')
except Exception as e:
	print('Error loading report: %s' %e.args)

try:
	# Put the parameters into a dictionary
	Parameters = {
		'clients': 'BASF',
		'projno' : 'T18087' 
	}
	
	RenderedReport = RS.RenderReport(LoadedReport=Report, format='PDF', parameters=Parameters)
except Exception as e:
	print('Error rendering report: %s' %e.args)


filename = os.path.join(os.path.dirname(__file__),'report'+ '.' + RenderedReport['Extension'])
fopen = open(filename, 'wb')
fopen.write(RenderedReport['Result'])

'''
	Testing GetParameters
'''
result	= RS.GetParameters('/DMS Reports/BEP Executive WCI Report')

for name in result :
	print('Name:', name)

'''
	Testing Find
'''
result = RS.Find(name='BEP Building Exec Summary', objtype='Report')

for key, value in result.items() :
		print('ID:', key)
		
		for key2, value2 in value.items():
			print(key2,':', value2)
		
		print('\n')

Methods = RS.ListServiceMethods()

if Methods:
    print(
        '''
        List of RPC Methods available on this SSRS version 
        Please see the MS docs to find out their usability
        '''
    )
    
    for i in Methods:
        print('>> ', i)

results = RS.ListExtensions('/DMS Reports/BEP Executive WCI Report')

for key, value in results.items() :
	print (value['Name'])
