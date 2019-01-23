#!/usr/bin/env python3
# Preprocess.py
'''program to clean and tokensize an Indic bible text before alignment
    author : kavitha raju
    input: specify lang and path of raw file in the main method
               -lang: mar|guj|hin
        .stem_a_word       -raw file: with one verse on one line. Total 7957 verses(having BCV at the line start, is okay)
    output: text file with cleaned
                   (punct, stopword, suffix, names removed) text in GIZA or efmaral formats
            object file of list of word tuples with info
                   (original_word,processed_word,found_alignment)
                   -if the word was removed, processed_word would be ""
                   -if the word was a name and its strongs is available, it will be in found_alignment''' 

import sys

import codecs
import string
import re
import pickle

class Preprocessor:

		def __init__(self,lang,path,lang_stopwords,lang_stemmer,lang_names):
			self.lang = lang

			self.stopwords = lang_stopwords
			self.names = lang_names
			self.stemmer = lang_stemmer
			self.path = path

			self.cleaned_bible = []

		def clean(self,stem_flag=True,stopword_flag=True,names_flag=True):
			file = codecs.open(self.path,mode="r",encoding="utf-8")
			
			punct = string.punctuation+"’‘“”।"
			
			bcv_pattern = re.compile("\d+,",re.UNICODE)
			bracket_pattern = re.compile("\([\s\w]+\)",re.UNICODE)



			self.cleaned_bible = []
			line = file.readline()
			line_num = 1
			

			while(line):

				bcv_match = re.match(bcv_pattern, line)
				if bcv_match:
					bcv = bcv_match.group(0)
					line  = line.replace(bcv,"")

				bracket_match = re.match(bracket_pattern,line)
				if bracket_match:
					bracket = bracket_match.group(0)
					line = line.replace(bracket," ")

				for pun in punct:
					line = line.replace(pun," ")

				line = re.split("\s+",line.strip())



				double_line = []
				for word in line:
					double_line.append((word,word))

				if stopword_flag == True:
					temp = double_line
					for sw in self.stopwords:
						for i,word_tuple in enumerate(temp):
							if word_tuple[1]==sw:
								double_line[i] = (word_tuple[0],'')
					
							

				if stem_flag == True:
					temp = double_line
					double_line = []
					for word_tuple in temp:
						if word_tuple[1]!="":
							stem = self.stemmer(word_tuple[1])
							# print(stem)
							double_line.append((word_tuple[0],stem))
						else:
							double_line.append(word_tuple)
					

				triple_line = []
				for word_tuple in double_line:
					new_tuple = (  word_tuple[0],  word_tuple[1] ,"" )
					triple_line.append(new_tuple)


				if names_flag == True:
					names_in_verse = [] 
					for ref_tuple in names_ref_list: 
						if ref_tuple[0]==line_num:
							names_in_verse.append((self.names[ref_tuple[2]],ref_tuple[2]))
							#thinking of adding name index(ref_tuple[2]) rather than the actual strong's num
						
					
					temp = triple_line
					triple_line = []
					for word_tuple in temp:
						if word_tuple[1]!="":
							for nam_pair in names_in_verse:
								if nam_pair[0] == "":
									continue
								elif "," in nam_pair[0]:
									name_forms = [x.strip() for x in re.split(",",nam_pair[0] )]
									for form in name_forms:
										if form == word_tuple[0]:
											# try exact match
											# print("EXACT MATCH:"+form+"-"+word_tuple[0])
											word_tuple = (word_tuple[0],"",nam_pair[1])
										elif word_tuple[0].startswith(form) or word_tuple[0].startswith(form[:-1]):
											# try partial match
											# print("PARTIAL MATCH:"+form+"-"+word_tuple[0])
											word_tuple = (word_tuple[0],"",nam_pair[1])										
								else:
									if nam_pair[0] == word_tuple[0]:
										# try exact match
										# print("EXACT MATCH:"+nam_pair[0]+"-"+word_tuple[0])

										word_tuple = (word_tuple[0],"",nam_pair[1])
									elif word_tuple[0].startswith(nam_pair[0]) or word_tuple[0].startswith(nam_pair[0][:-1]):
										# try partial match
										# print("PARTIAL MATCH:"+nam_pair[0]+"-"+word_tuple[0])
										word_tuple = (word_tuple[0],"",nam_pair[1])
						triple_line.append(word_tuple)
					



				self.cleaned_bible.append(triple_line)
				line = file.readline()
				line_num = line_num+1



			# print("Cleaned the text and writing outputs...")

			file = open("../Models/preprocessed_bible.pkl","wb")
			pickle.dump(self.cleaned_bible,file)
			file.close

					

		def get_clean_text(self,stem_flag=True,stopword_flag=True,names_flag=True):
			
			self.clean(stem_flag,stopword_flag,names_flag)


			clean_text = []
			for verse in self.cleaned_bible:

				clean_verse = ""
				for word_tuple in verse:
					if word_tuple[1] != "":
						clean_verse  = clean_verse+" "+word_tuple[1]
				clean_text.append(clean_verse)
						

			return clean_text

		def suffix_analysis(self):
			bible = self.get_clean_text(stem_flag=False,stopword_flag=True,names_flag=False)

			
			all_possible_suffixes = {}

			for line in bible:
				for word in re.split("\s+",line.strip()):

					possible_suffixes = [word[i:] for i in range(len(word))]

					for suf in possible_suffixes:
						if suf in all_possible_suffixes:
							all_possible_suffixes[suf] += 1
						else:
							all_possible_suffixes[suf] = 1

			sorted_possible_siffixes = []

			for key, value in sorted(all_possible_suffixes.items(),reverse=True, key=lambda kv: kv[1]):
				sorted_possible_siffixes.append( (key, value))


			most_frequent = sorted_possible_siffixes[:250]
			print("suffix\tfrequency")
			for suf,freq in most_frequent:
				cur_index = most_frequent.index((suf,freq))
				drop = False
				for other_suf,_other_freq in most_frequent[cur_index+1:]:
					if other_suf.endswith(suf):
						drop = True
						break
				if drop:
					pass
				else:
					print(suf+"\t"+str(freq))


					

			
		def get_stats(self):

			punct_removed_bible = self.get_clean_text(stem_flag=False,stopword_flag=False,names_flag=False)
			punct_sw_removed_bible = self.get_clean_text(stem_flag=False,stopword_flag=True,names_flag=False)
			punct_sw_suffix_removed_bible = self.get_clean_text(stem_flag=True,stopword_flag=True,names_flag=False)
			punct_sw_suffix_names_removed_bible = self.get_clean_text(stem_flag=True,stopword_flag=True,names_flag=True)



			bibles = [
						punct_removed_bible,
						punct_sw_removed_bible,
						punct_sw_suffix_removed_bible,
						punct_sw_suffix_names_removed_bible
						]

			for bib in bibles:
				total_words = 0
				unique_words = 0
				vocab = []

				for line in bib:
					for word in re.split("\s+",line):
						total_words = total_words+1
						if word not in vocab:
							vocab.append(word)
				unique_words = len(vocab)

				print("total_words: "+str(total_words))
				print("unique_words: "+str(unique_words))
				print("********\n")
		
		def get_high_freq_words(self):

			punct_removed_bible = self.get_clean_text(stem_flag=False,stopword_flag=False,names_flag=False)
			
			total_words = 0
			unique_words = 0
			vocab = {}

			for line in punct_removed_bible:
				for word in re.split("\s+",line):
					total_words = total_words+1
					if word not in vocab:
						vocab[word] = 1
					else:
						vocab[word] += 1
			sorted_vocab = []
			for key, value in sorted(vocab.items(), key=lambda kv: kv[1]):
				sorted_vocab.append( (key, value))
			print("word\tfreq")
			for word,freq in sorted_vocab[-100:]:
				print(word+"\t"+str(freq))


if __name__ == '__main__':



	if len(sys.argv)>=3:
		lang  = sys.argv[1]
		path = sys.argv[2]
		package1 = 'stopword_lookup'
		name1 = lang+"_stopwords"

		lang_stopwords = getattr(__import__(package1, fromlist=[name1]), name1)
		
		package2 = 'name_lookup'
		name2 = lang+"_names"

		lang_names = getattr(__import__(package2, fromlist=[name2]), name2)

		sys.path.append('./stemmers')


		package3 = lang+'_stemmer'
		name3 = 'stem'

		lang_stemmer = getattr(__import__(package3, fromlist=[name3]), name3)

		lang_obj = Preprocessor(lang,path,lang_stopwords,lang_stemmer,lang_names)

		sw_flag = False
		stem_flag = False
		ne_flag = False

		status_flag=False
		suffix_anal_flag=False
		stop_anal_flag=False

		if len(sys.argv)>3:
			params = sys.argv[3:]
			for i,val in enumerate(params):
				if val == "-sw":
					sw_flag = True
				elif val == "-stm":
					stem_flag = True
				elif val == "-ne":
					ne_flag = True
				elif val == "-stats":
					status_flag = True
				elif val == '-suffix_anal':
					suffix_anal_flag = True
				elif val == '-stop_anal':
					stop_anal_flag = True
				else:
					print("Incorrect option. See usage by typing 'python3 Preprocessor'")
					sys.exit(1)

		if lang=="grk" and stem_flag==True:
			print("Using strongs instead of Greek words. So need to stem further!!!")
			stem_flag=False
		if status_flag == True:
			lang_obj.get_stats()
			sys.exit(0)

		if suffix_anal_flag == True:
			lang_obj.suffix_analysis()
			sys.exit(0)

		if stop_anal_flag == True:
			lang_obj.get_high_freq_words()
			sys.exit(0)


		

		print("Cleaning bible text")
		cleaned_lang = lang_obj.get_clean_text(stem_flag=stem_flag,stopword_flag=sw_flag,names_flag=ne_flag)

		print("Got cleaned text: "+lang)
		outfile = "../Resources/parallel_corpus_GIZAformat.txt"
		pc_giza = codecs.open(outfile,mode="w",encoding="utf-8")
		for sent in cleaned_lang:
			pc_giza.write(sent+"\n")
		pc_giza.close()

		print("Cleaned verses written to: "+outfile)
	
	else:
		print("Correct format: python3 Preprocessor lang path [-sw] [-stm] [-ne]\n"+
		             " or\n python3 Preprocessor lang path [-stats]\n"+
		             "lang take 3 letter code for language like grk, hin, mar, guj etc\n"+
		             "path is the path to the raw file\n"+
		             "stopword removal(-sw), stemming(-stm) and names removal(-ne)\n"+
		             " options can be turned on by specifying them(default is False)\n")












