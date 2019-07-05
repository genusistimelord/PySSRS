# -*- coding: utf-8 -*-

from suds.client import Client
from suds.sax.text import Text
from suds.sax.element import Element
from suds.transport.http import HttpAuthenticated
import requests
from requests_ntlm import HttpNtlmAuth
import suds_requests
from . import schemas
import base64
import logging as log
import codecs
import uuid
import sys
import os
from _ast import Load

class SSRS():
	'''
	Create a SOAP connection to a SSRS (Microsoft Reporting Services)

	Example of usage on SSRS 2008:
		RS = SSRS(ReportService	  = 'http://localhost/ReportinServices/ReportService2010.asmx?wsdl', 
				  ReportExecution = 'http://myserver/reportserver/ReportExecution2005.asmx?wsdl',
				  user			  = 'user@domain.com', 
				  key_password	  = 'myfreakingpassword'
				  domain		  = 'mydomain'
				)

	'''

	def __init__(self, ReportService, ReportExecution, user, key_password, domain=None, verbose=True):
		
		self.verbose = verbose
		servsession = requests.Session()
		execsession = requests.Session()
		log.basicConfig(filename = 'SSRS.log', level = log.INFO)

		if domain:
			user = '{}\\{}'.format(domain, user)
			servsession.auth = HttpNtlmAuth(user, key_password)
			execsession.auth = HttpNtlmAuth(user, key_password)
		else: 
			servsession.auth = (user, key_password)
			execsession.auth = (user, key_password)

		try:
			self.ServiceClient = Client(ReportService, transport = suds_requests.RequestsTransport(servsession))
			self.ExecutionClient = Client(ReportExecution, transport = suds_requests.RequestsTransport(execsession))
		except Exception as e:		  
			msg = "Error during connection: %s" % e.args
			log.error(msg)			
		
			if self.verbose: 
				print(msg)
				
			exit() 

	def ListServiceMethods(self):
		'''
		Return the list of methods available for your SSRS Service version
		'''
		try:
			list_of_methods = [method for method in self.ServiceClient.wsdl.services[0].ports[0].methods]
			return list_of_methods

		except Exception as e:
			msg = "ListServiceMethods() Could not retrieve the methods: %s" % e.args	 
			log.error(msg)			  
			
			if self.verbose: 
				print(msg)
				
			return False
	
	def ListExecutionMethods(self):
		'''
		Return the list of methods available for your SSRS Execution version
		'''
		try:
			list_of_methods = [method for method in self.ExecutionClient.wsdl.services[0].ports[0].methods]
			return list_of_methods

		except Exception as e:
			msg = "ListExecutionMethods() Could not retrieve the methods: %s" % e.args	 
			log.error(msg)			  
			
			if self.verbose: 
				print(msg)
				
			return False

	def ListDirItems(self, dir = r'/', recursive=False):
		'''
		List all itens in a folder. 
		if specified the <recursive> parameter, subfolders will be scanned too
		'''
		try:
			it = self.ServiceClient.service.ListChildren(dir, recursive)
			it = it.CatalogItem
		except Exception as e:
			msg = "ListDirItems() Could not retrieve the Objects: %s" % e.args
			log.error(msg)
			
			if self.verbose:	 
				print(msg)
				
			return False

		catalog_dict = {}
		
		for item in it:
			catalog_dict[item['ID']] = {
					'Name'			: item['Name'],
					'Path'			: item['Path'],
					'TypeName'		: item['TypeName'],
					'CreationDate'	: item['CreationDate'],
					'ModifiedDate'	: item['ModifiedDate'],
					'CreatedBy'		: item['CreatedBy'],
					'ModifiedBy'	: item['ModifiedBy'],
					'ItemMetadata'	: item['ItemMetadata'],
				}
		
		return catalog_dict

	def Find(self, name, objtype = None):		
		'''
		Find objects on SSRS 
		'''
		try: 
			it = self.ListDirItems(recursive = True)
		except Exception as e:
			msg = "Find() Could not retrieve the Objects: %s" % e.args
			log.error(msg)
			
			if self.verbose:	 
				print(msg)	
				
			return
		
		catalog_dict = {}
		for key, value in it.items() :
			for word in value.values():
				if name in str(word):
					if objtype == None:
						catalog_dict[key] = value
					elif it[key]['TypeName'] == objtype:
						catalog_dict[key] = value
		
		return catalog_dict

	def GetParameters(self, path):
		'''
		Retrieve parameters from an SSRS Report
		'''
		try:
			it = self.ServiceClient.service.GetItemParameters(path, None, True, None, None)
		except Exception as e:
			msg = "GetParameters() Could not retrieve the parameters: %s" % e.args
			log.error(msg)
			if self.verbose:
				print(msg)
				return
			  
		param_dict = {}
		for item in it.ItemParameter:
			param_dict[item['Name']] = {
				 'ParameterTypeName'		: item['ParameterTypeName'],
				 'Nullable'					: item['Nullable'],
				 'AllowBlank'				: item['AllowBlank'],
				 'MultiValue'				: item['MultiValue'],
				 'QueryParameter'			: item['QueryParameter'],
				 'Prompt'					: item['Prompt'],
				 'PromptUser'				: item['PromptUser'],
				 'ValidValuesQueryBased'	: item['ValidValuesQueryBased'],
				 'DefaultValuesQueryBased'	: item['DefaultValuesQueryBased'],
			}
		
		return param_dict

	def ListExtensions(self, path):
		'''
		Retrieve Usable Render Extensions
		'''
		try:
			it = self.ServiceClient.service.ListExtensions("Render")
		except Exception as e:
			msg = "ListExtensions() Could not retrieve the Extensions: %s" % e.args
			log.error(msg)
			if self.verbose:
				print(msg)
				return
		
		ext_dict = {}
		for item in it.Extension:
			ext_dict[item['Name']] = {
				 'Name'							: item['Name'],
				 'LocalizedName'				: item['LocalizedName'],
				 'Visible'						: item['Visible'],
				 'IsModelGenerationSupported'	: item['IsModelGenerationSupported'],
			}

		return ext_dict

	def RequestReport(self, path):
		try:
			return self.ExecutionClient.service.LoadReport(path, None)
		except Exception as e:
			msg = "Could not Load the Report: %s" % e.args
			log.error(msg)
			
			if self.verbose:	 
				print(msg)
			
			return
	
	def RenderReport(self, LoadedReport, format, **parameters):
		'''
		Render an already executed Report
		'''
		# check if format is valid
		available_formats = ['XML','NULL','CSV','IMAGE','PDF','HTML4.0', 'HTML3.2','MHTML','EXCEL','Word']

		if format not in available_formats:
			msg = "Format is not valid: %s" % format
			log.error(msg)
			
			if self.verbose:	 
				print(msg)
			
			return
		
		# Set parameters
		params = ''
		for k, v in parameters['parameters'].items():
			params =  params +'''
			<rep:ParameterValue>
			   <rep:Name>%s</rep:Name>
			   <rep:Value>%s</rep:Value>
			</rep:ParameterValue>
			''' % (k, v)
		
		param_xml = schemas.xml_Execute_Report_Parameter  
		param_xml = param_xml.format(LoadedReport.ExecutionID, params)
		
		try:
			setparam = self.ExecutionClient.service.SetExecutionParameters(__inject={'msg': param_xml})
		except Exception as e:
			msg = "Could not Send Parameters: %s" % e.args
			log.error(msg)
			
			if self.verbose:	 
				print(msg) 
			
			return
		
		# Default XML Schema | SUDS Factory doesent worked very well in this case
		xml = schemas.xml_Render_Report.format(LoadedReport.ExecutionID, format)
		
		# Render the report by its ExecutionID
		try:
			result = self.ExecutionClient.service.Render(__inject={'msg': xml})
		except Exception as e:
			msg = "Could not Render the Report: %s" % e.args
			log.error(msg)
			
			if self.verbose:	 
				print(msg) 
			
			return
		
		# Data to be sended
		Data = {}
		for k, v in result:
			if k == 'Result':
				 Data['Result'] = base64.b64decode(result.Result)
			else:
				Data[k] = v

		return Data
	
	def FlushCache(self, report):
		try:
			self.ServiceClient.service.FlushCache(report)
		except Exception as e:
			msg = "Could not Flush the Cache: %s" % e.args
			log.error(msg)
			
			if self.verbose:
				print(msg)

			return
	
	def FlushMultiCache(self, reports):
		try:
			for report in reports:
				self.ServiceClient.service.FlushCache(report)
		except Exception as e:
			msg = "Could not Flush the Cache: %s" % e.args
			log.error(msg)
			
			if self.verbose:
				print(msg)

			return
		
		
		