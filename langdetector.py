#!/usr/bin/env python3
# -*- coding: utf-8 -*-

  

import json
import os

def load_jsons_from_dir(directory):
	jsons = {}
	for f in os.listdir(directory):
		if f.endswith(".json"):
			jsons[f[:2]]=json.load(open(directory+"/"+f,"r"))
	return jsons



class LanguageDetector(object):
	
	def __init__(self):
		self.load_langs_dict()
		self.methods = []
		self.compound_methods = ["average","max"]
		self.load_corpus_dict("smallwords","corpus/smallwords")
		self.load_corpus_dict("trigrams","corpus/trigrams") 

				
	def __clean_text(self,text):
		chars = u'.,;:¡!¿?1234567890-_+-=()[]<>{}\|/""*@#$%&~'+u"'"
		t = text
		for a in chars:
			t = t.replace(a,'')
		return t.lower()

			
	def __get_trigrams(self,text):
		return [text[i:i+3] for i in range(0,len(text)-2)]

		
	def __get_smallwords(self,text):
		t = text.split(' ')
		return [i for i in t if len(i)<=5 and i!='']

		
	def load_langs_dict(self,iso_json_file="corpus/iso-639-2-language-code.json"):
		self.langs = json.load(open(iso_json_file,"r"))	


	def __detect_by_smallwords(self,text):
		t = self.__clean_text(text)
		sw = self.__get_smallwords(t)
		counter = {lang:0 for lang in self.corpus_smallwords.keys()}
		for word in sw:
			for lang,words in self.corpus_smallwords.items():
				if word in words:
					counter[lang] = counter[lang]+1
		swc = 1 if len(sw)==0 else len(sw)
		return {e[0]:e[1]*100.0/(swc) for e in counter.items()}

			
	def __detect_by_trigrams(self,text):
		t = self.__clean_text(text)
		tg = self.__get_trigrams(t)
		counter = {lang:0 for lang in self.corpus_trigrams.keys()}
		for word in tg:
			for lang,words in self.corpus_trigrams.items():
				if word in words:
					counter[lang] = counter[lang]+1
		return {e[0]:e[1]*100.0/len(tg) for e in counter.items()}		
		
		
	def __compound_average(self,methods,text):
		results = []
		langs_set = []
		for method in methods:
			result = eval("self.detect_by_"+method+"(text)")
			results.append(result)
			langs_set.append(set(result.keys()))
		langs = set()
		for s in langs_set:
			if len(langs)==0:
				langs = langs.union(s)
			else:
				langs = langs.intersection(s)
		rave = {}
		for lang in langs:
			for result in results:
				if lang in rave:
					rave[lang] = rave[lang]+result[lang]
				else:
					rave[lang] = result[lang]
		return {r[0]:r[1]/len(results) for r in rave.items()}
		
		
	
	def __compound_max(self,methods,text):
		results = []
		for method in methods:
			results.append(eval("self.detect_by_"+method+"(text)"))
		rmax = {}
		for result in results:
			for lang in result:
				if lang in rmax:
					if result[lang]>rmax[lang]:
						rmax[lang]=result[lang]
				else:
					rmax[lang]=result[lang]
		return rmax
		
					
	
	
	def compound_detection(self,compound_method,methods,text):
		return eval("self._LanguageDetector__compound_"+compound_method+"(methods,text)")

	
	def load_corpus_dict(self,method,directory):		
		jsons = load_jsons_from_dir(directory)
		if len(jsons)>0:
			if not method in self.methods:
				self.methods.append(method)
			setattr(self,"corpus_"+method,jsons)
			if not hasattr(LanguageDetector,"detect_by_"+method):
				setattr(LanguageDetector,"detect_by_"+method,getattr(LanguageDetector,"_LanguageDetector__detect_by_"+method))
		else:
			if method in self.methods:
				self.methods.remove(method)
			if hasattr(self,"corpus_"+method):
				delattr(self,"corpus_"+method)
			if hasattr(LanguageDetector,"detect_by_"+method):
				delattr(LanguageDetector,"detect_by_"+method)
	
		
def main():
	ld =  LanguageDetector()
	import argparse
	parser = argparse.ArgumentParser(description="Language detector")
	parser.add_argument("text",help="Text or Text File for language detection",metavar="TEXT",nargs="?")
	parser.add_argument("-c","--compound",help="Compound method to use if multiple detection methods are setted",metavar="CMETHOD",choices=ld.compound_methods)
	parser.add_argument("-m","--methods",help="Method or Methods to use for detection",metavar="METHOD",choices=ld.methods,nargs="+",default=["trigrams"])
	parser.add_argument("-u","--unique",help="Unique result",action="store_false")
	
	args = parser.parse_args()
	
	if args.compound!=None:
		print("Method: "+args.compound)
		result = ld.compound_detection(args.compound,args.methods,args.text).items()
		if not args.unique:
			result =  [max(result,key=lambda x:x[1])]
		for r in result:
			print(ld.langs[r[0]]+"("+r[0]+")"+":"+str(r[1])) 
			
	else:
		for m in args.methods:
			print("Method: "+m)
			result = (eval("ld.detect_by_"+m+"(u'"+args.text+"')")).items()
			if not args.unique:
				result =  [max(result,key=lambda x:x[1])]
			for r in result:
				print(ld.langs[r[0]]+"("+r[0]+")"+":"+str(r[1]))
	
	return 0

if __name__ == '__main__':
	main()

