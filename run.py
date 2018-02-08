#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import gzip
import warc
import sys
from collections import defaultdict
from pyspark import SparkContext, SparkConf

data_path=sys.argv[3]

if sys.argv[2]=='A':
	low_threshold=10
else:
	low_threshold=30

f=open(sys.argv[5],'r')
stop_words={}
for line in f:
	stop_words[line.strip()]=1
f.close()

def Standardize(token):
	result=token.strip("-'"+'"')
	for i in result:
		if i.isalpha() or i=="-" or i=="'":
			continue
		else:
			return ""
	return result.lower()

def word_docid_n(wet_file):
	gzip_fobj = gzip.open(wet_file, "r")
	warc_fobj = warc.WARCFile(fileobj=gzip_fobj, compress=False)

	result=[]
	i=0
	for record in warc_fobj:
		try:
			if "WARC-Type" in record:
				if record["WARC-Type"] == "conversion":
					payloads = record.payload.read().split()
					temp_sum = 0
					save_word={}
					for word in payloads:
						my_word = Standardize(word).lower()
						if len(my_word)!=0:
							temp_sum += 1
							save_word[my_word]=save_word.get(my_word,0)+1
					if temp_sum > 10:
						result.extend([(w,(record["WARC-Record-ID"],save_word[w],1)) for w in save_word])
		except Exception as e:
			pass
	return result

def del_stop_word(my_input):
	if stop_words.get(my_input[0],0)==0:
		return True
	else:
		return False
	
def word_doc_n(my_input):
	return (my_input[1][0],(my_input[0],my_input[1][1]))

def doc_n(my_input):
	return (my_input[1][0],my_input[1][1])

def word_1(i):
	return (i[0],i[1][2])

def word_n(i):
	return (i[0],i[1][1])

def doc_word(i):
	return (i[1][0],i[0])

global raw_doc_num

def find_high_freq(my_input):
	if my_input[1]>=(raw_doc_num*0.9):
		return True
	else:
		return False

def find_low_freq(my_input):
	if my_input[1]<low_threshold:
		return True
	else:
		return False

def get_0(my_input):
	return my_input[0]

def get_1(my_input):
	return my_input[1]

def switch(my_input):
	return (my_input[1],my_input[0])

wf=[]
f=open(sys.argv[4],'r')
for line in f:
	wf.append(data_path+line.strip())
f.close()
#print wf
#print "------------------------------------------------"
#wf=["CC-MAIN-20161202170900-00000-ip-10-31-129-80.ec2.internal.warc.wet.gz"]
sc = SparkContext('local','proj2')
Wet_file=wf
wetfile= sc.parallelize(Wet_file)

records11=wetfile.flatMap(word_docid_n)
WORD_DOCID_N=records11.filter(del_stop_word)

WORD_1=WORD_DOCID_N.map(word_1)

DOC_WORD=WORD_DOCID_N.map(doc_word).persist()

WORD_N=WORD_DOCID_N.map(word_n).persist()

raw_doc_freq=WORD_1.reduceByKey(lambda a, b: a + b).persist()

raw_doc_num=len(WORD_DOCID_N.countByKey())

high_freq=raw_doc_freq.filter(find_high_freq)
low_freq=raw_doc_freq.filter(find_low_freq)

word_n_del=WORD_N.subtractByKey(high_freq).subtractByKey(low_freq)
# (key, tf in one all)

n=raw_doc_freq.subtractByKey(high_freq).subtractByKey(low_freq)
N1=n.collect()
D=n.sortByKey().map(get_0).zipWithIndex()
Dictionary=D.collect()
WORD_N_DEL=word_n_del.reduceByKey(lambda a, b: a + b).persist()
w=WORD_N_DEL.collect()
# (key, tf in all)
TOKEN_NUM=sum([ww[1] for ww in w])

WORD_DOC_N_Del=WORD_DOCID_N.subtractByKey(low_freq).subtractByKey(high_freq)
DOC_N=WORD_DOC_N_Del.map(doc_n)

d=DOC_N.reduceByKey(lambda a, b: a + b).collect()

word_doc_del=DOC_WORD.map(switch).subtractByKey(low_freq).subtractByKey(high_freq)
DOC_LEN=word_doc_del.map(switch).countByKey()

DL=[i[1] for i in d]

DOC_LEN_AVE=int(sum(DL)*1.0/len(DOC_LEN))

DL.sort()

DOC_LEN_MAX=DL[-1]
DOC_LEN_MIN=DL[0]
i10=int(len(DOC_LEN)*0.1)
i30=int(len(DOC_LEN)*0.3)
i50=int(len(DOC_LEN)*0.5)
i70=int(len(DOC_LEN)*0.7)
i90=int(len(DOC_LEN)*0.9)
i99=int(len(DOC_LEN)*0.99)

'''(word,(doc,n))=>(doc(word,n))'''
def to_doc_word_n(my_input):
	return (my_input[1][0][0],(my_input[1][1],my_input[1][0][2]))#!!!!!!

all_freq=WORD_N_DEL.join(n).sortByKey().collect()

DOC_WORD_N_DEL=WORD_DOC_N_Del.join(D).map(to_doc_word_n).collect()

d=defaultdict(list)
for (i,j) in DOC_WORD_N_DEL:
	d[i].append(j)

file_name="processed_corpus/pairs"
out_pairs = open(file_name, 'w')
for i in d:
	t=0
	temp=''
	for j in d[i]:
		if t==0:
			temp = str(j[0]) + ":" + str(j[1])
			t=1
		else:
			temp+=' '+str(j[0]) + ":" + str(j[1])
	temp+='\n'
	out_pairs.write(temp)
out_pairs .close()

out_statistics = open("statistics",'w')
temp='Number of Words: '+str(len(N1))+'\n'
temp+='Number of Documents: '+str(len(DL))+'\n'
temp+='Number of Tokens: '+str(TOKEN_NUM)+'\n'
temp+='Maximum Document Length: '+str(DOC_LEN_MAX)+'\n'
temp+='Minimum Document Length: '+str(DOC_LEN_MIN)+'\n'
temp+='Average Document Length: '+str(DOC_LEN_AVE)+'\n'
temp+='Document Length 10th percentile: '+str(DL[i10])+'\n'
temp+='Document Length 30th percentile: '+str(DL[i30])+'\n'
temp+='Document Length 50th percentile: '+str(DL[i50])+'\n'
temp+='Document Length 70th percentile: '+str(DL[i70])+'\n'
temp+='Document Length 90th percentile: '+str(DL[i90])+'\n'
temp+='Document Length 99th percentile: '+str(DL[i99])
#temp+="\n"+str(raw_doc_num)
out_statistics.write(temp)
out_statistics.close()

out_dictionary = open("dictionary",'w')

for i in range(len(Dictionary)):
	temp=str(Dictionary[i][0])+"\t"+str(Dictionary[i][1])+"\n"
	out_dictionary.write(temp)

out_dictionary .close()

out_frequency = open("frequency",'w')

for i in range(len(all_freq)):
	temp=str(all_freq[i][0])+"\t"+str(all_freq[i][1][0])+"\t"+str(all_freq[i][1][1])+"\n"
	out_frequency.write(temp)
out_frequency .close()

print "ok"
sc.stop()








