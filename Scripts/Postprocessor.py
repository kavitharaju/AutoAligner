#!/usr/bin/env python3
# Postprocessor.py
'''program to map the obtained aligments for the filtered text, 
				   back to the positions in the original verse
		   to combine the sure alignments(names) from preprocessing 
				   with the obtained alignments
				   it also writes the titus portion of aligned text seperately
								   in a file for evaluation

		Additionally added: translation word look up and pronoun look up

'''



import pickle,sys,re,itertools

cmd_line_params = sys.argv

if len(cmd_line_params) >= 3:
	src_lang = cmd_line_params[1]
	trg_lang = cmd_line_params[2]


	package1 = 'name_lookup'
	name1 = src_lang+"_names"
	name10 = trg_lang+"_names"

	src_names = getattr(__import__(package1, fromlist=[name1]), name1)
	trg_names = getattr(__import__(package1, fromlist=[name10]), name10)

	package2 = 'tw_lookup'
	name2 = src_lang+"_tws"
	name20 = trg_lang+"_tws"

	src_tw = getattr(__import__(package2, fromlist=[name2]), name2)
	trg_tw = getattr(__import__(package2, fromlist=[name20]), name20)

	package3 = 'pronoun_lookup'
	name3 = src_lang+"_pronouns"
	name30 = trg_lang+"_pronouns"

	src_prn = getattr(__import__(package3, fromlist=[name3]), name3)
	trg_prn = getattr(__import__(package3, fromlist=[name30]), name30)

	
else:
	print("Usage: python3 Postprocessor src trg [-tw] [-prn] [-NT]\n "+
				"src and trg takes 3 letter language codes like grk, hin, etc.\n"+
				"specify if translation words or pronoun look up is to be used.\n"+
				"Default values are False\n"+
				"If the alignement is only for NT, specify that also, so that lids can be started from 23146\n")
	sys.exit(1)

tw_flag = False
prn_flag = False
NT = False

output_pickle_file_name = '../Models/'+src_lang+"_"+trg_lang+"_pos_pairs.pkl"


if len(cmd_line_params)>3:
	params = cmd_line_params[3:]
	for i,val in enumerate(params):
		if val == "-tw":
			tw_flag = True
		elif val == "-prn":
			prn_flag = True
		elif val == "-NT":
			NT = True
		elif val == "-h" or val == "-help":
			print("Usage: python3 Postprocessor src trg [-tw] [-prn]\n "+
				"src and trg takes 3 letter language codes like grk, hin, etc.\n"+
				"specify if translation words or pronoun look up is to be used.\n"+
				"Default values are False\n")
			sys.exit(1)
		elif val == "-o":
			pos = cmd_line_params.index("-o") + 1
			output_pickle_file_name = cmd_line_params.pop(pos)
			print(output_pickle_file_name)
		else:
			pass




src_prepro_file = open("../Models/"+src_lang+".preprocessed_bible.pkl","rb")
trg_prepro_file = open("../Models/"+trg_lang+".preprocessed_bible.pkl","rb")

pospair_file = open("../Models/partial_pos_pair.pkl","rb")

outfile = open("../Resources/"+src_lang+"_"+trg_lang+"_complete_pos_pairs.txt","w")
# evalfile = open("../Resources/titus_for_eval.wa","w")

preprocessed_src = pickle.load(src_prepro_file)
preprocessed_trg = pickle.load(trg_prepro_file)


partial_pos_pairs = pickle.load(pospair_file)


######### code portion adds the stop words ############
######### and names removed earlier and    ############
######### adjusts the pos-pair values      ############
######### accordingly(this is mandatory step)##########

temp = partial_pos_pairs
partial_pos_pairs = []
prev_verse_num=0
verse_pos_pair_list = []
for pair in temp:
	verse_num = pair[0]
	if verse_num != prev_verse_num:
		#start of new vesre
		partial_pos_pairs.append(verse_pos_pair_list)
		verse_pos_pair_list = []
	
	verse_pos_pair_list.append((pair[1],pair[2]))
	prev_verse_num = verse_num


partial_pos_pairs.append(verse_pos_pair_list)



partial_pos_pairs = partial_pos_pairs[1:]

complete_pos_pairs = []
error_count = 0

verse_counter_src = 0
verse_counter_trg = 0
verse_counter_alignment = 0
print('Processing positional pairs:')
while verse_counter_src<len(preprocessed_src) and verse_counter_trg< len(preprocessed_trg) and verse_counter_alignment< len(partial_pos_pairs):
	src = preprocessed_src[verse_counter_src]
	trg = preprocessed_trg[verse_counter_trg]
	alignments = partial_pos_pairs[verse_counter_alignment]	
	print(".",end='')

	original_src = [x[0] for x in src]
	used_src = [x[1] for x in src]
	while True:
		if "" in used_src:
			used_src.remove("")
		else:
			break
	
	original_trg = [x[0] for x in trg]
	used_trg = [x[1] for x in trg]
	while True:
		if "" in used_trg:
			used_trg.remove("")
		else:
			break
	
	new_alignments =[]

	for i,word_tuple in enumerate(src):
		# case: stop word was removed for alignment
		if word_tuple[1] == "" and word_tuple[2]=='':
			new_alignments.append((i,255))
			
		# case: NE was removed for alignment; its index is given in column 3(word_tuple[2])
		elif word_tuple[1] == "":
			try:
				trg_word = trg_names[word_tuple[2]]
				trg_pos = None
				if "," in trg_word:
					trg_words = [n.strip() for n in re.split(",",trg_word)]
				else:
					trg_words = [trg_word.strip()]
				for trg_word in trg_words:
					if trg_word == "":
						pass
					elif trg_word in original_trg:
						trg_pos = original_trg.index(trg_word)
						break
					else:
						for k,w in enumerate(original_trg):
							if w.startswith(trg_word):
								trg_pos = k
								break
						if trg_pos == None:
							for k,w in enumerate(original_trg):
								if w.startswith(trg_word[:-1]):
									trg_pos = k
									break
				if trg_pos !=None:
					new_alignments.append((i,trg_pos))
				
			except Exception as e:
				print(src)
				print(trg)
				print(word_tuple[2])
				raise e 



	for i,word_tuple in enumerate(trg):
		if word_tuple[1] == "" and word_tuple[2]=='':
			new_alignments.append((255,i))

	#case:the line given to aligner was empty and was omitted while aligning
	if  "".join(used_src)=="" or "".join(used_trg)=="":
		verse_counter_alignment=verse_counter_alignment-1
	else:

		# case: alignment is obtained by giza; but positions are not as per the original verse
		for xy in alignments:
			try:
				used_src_pos = xy[0]
				used_trg_pos = xy[1]
				src_word = used_src[used_src_pos]
				trg_word = used_trg[used_trg_pos]
				
				
				src_count = used_src.count(src_word)
				trg_count = used_trg.count(trg_word)

				correct_srcpos = None
				indices_inused = [i for i, x in enumerate(used_src) if x == src_word]
				occurence = indices_inused.index(used_src_pos)
				count =0
				for i,tpl in enumerate(src):
					if tpl[1]==src_word:
						if occurence == count:
							# print(src_word+"found in src")
							correct_srcpos = i
						else:
							count+=1
			
				correct_trgpos = None
				indices_inused = [i for i, x in enumerate(used_trg) if x == trg_word]
				occurence = indices_inused.index(used_trg_pos)
				count =0
				for i,tpl in enumerate(trg):
					if tpl[1]==trg_word:
						if occurence == count:
							correct_trgpos = i
							# print(trg_word+"found in trg")
						else:
							count+=1
				

				if(correct_srcpos==None or correct_trgpos==None):
					print("could not find positions!!!")
					sys.exit(0)
				new_alignments.append((correct_srcpos,correct_trgpos))

				
			except Exception as e:
				print(e)
				print("verse_counter_src:"+str(verse_counter_src))
				print ("at verse: "+' '.join(original_src))
				print ("at verse: "+' '.join(original_trg))
				print ("at verse: "+' '.join(used_src))
				print(used_trg)
				print(used_src_pos,used_trg_pos)
				print(alignments)
				error_count=error_count+1
				print("Erro count:"+str(error_count))
				raise e

	complete_pos_pairs.append(new_alignments)
	verse_counter_alignment+=1
	verse_counter_trg+=1
	verse_counter_src+=1
	

############## code portion of adding back stopwords ####################
############## and names ends here                   ####################




final_complete_pos_pairs = complete_pos_pairs
#################### code to check for translation ##############
#################### words in the verses and 	   ##############
#################### make adjustments in the pos-  ##############
#################### pair values                   ##############
if tw_flag == True or prn_flag == True:
	src_lookup_to_use = []
	trg_lookup_to_use = []

	if tw_flag == True:
		print("Using translation words Lookup")
		src_lookup_to_use = src_lookup_to_use + src_tw
		trg_lookup_to_use = trg_lookup_to_use + trg_tw

	if prn_flag == True:
		print("Using Pronoun Lookup")
		src_lookup_to_use = src_lookup_to_use + src_prn
		trg_lookup_to_use = trg_lookup_to_use + trg_prn
	


	final_complete_pos_pairs = []
	for src,trg,pos_pairs in zip(preprocessed_src,preprocessed_trg,complete_pos_pairs):
		split_src_verse = ["".join(x[0]) for x in src]
		split_trg_verse = ["".join(y[0]) for y in trg]
		src_verse = " ".join(split_src_verse)
		trg_verse = " ".join(split_trg_verse)

		candidate_tw_matches = []

		for index,tw_list_src in enumerate(src_lookup_to_use):
			for tw_src in tw_list_src:
				if tw_src in src_verse:


					src_indices_probable = []
					for wrd in re.split(" ",tw_src):
						curr_wrd_indices = [i for i, x in enumerate(split_src_verse) if x == wrd]
						src_indices_probable.append(curr_wrd_indices)
					src_probable_seq = list(itertools.product(*src_indices_probable))
					refined_src_probable_seq = src_probable_seq
					for seq in src_probable_seq:
						prev = seq[0]-1
						for pos in seq:
							# to keep only consecutive positions
							if pos == prev+1:
								prev = pos
							else:
								refined_src_probable_seq.remove(seq)
								break


					tw_list_trg = trg_lookup_to_use[index]
					for tw_trg in tw_list_trg:
						if tw_trg in trg_verse:



							trg_indices_probable = []
							for wrd in re.split(" ",tw_trg):
								curr_wrd_indices = [i for i, x in enumerate(split_trg_verse) if x == wrd]
								trg_indices_probable.append(curr_wrd_indices)
							trg_probable_seq = list(itertools.product(*trg_indices_probable))
							refined_trg_probable_seq = trg_probable_seq
							for seq in trg_probable_seq:
								prev = seq[0]-1
								for pos in seq:
									# to keep only consecutive positions
									if pos == prev+1:
										prev = pos
									else:
										refined_trg_probable_seq.remove(seq)
										break
							matches = list(itertools.product(refined_src_probable_seq,refined_trg_probable_seq))
							candidate_tw_matches.append(matches)

		sure_tw_matches = []
		for match_pair_list in candidate_tw_matches:
			for match_pair in match_pair_list:
				src_pos = match_pair[0]
				trg_pos = match_pair[1]
				for i,j in itertools.product(src_pos,trg_pos):
					if (i,j) not in sure_tw_matches:
						sure_tw_matches.append((i,j))

		
		sure_src_positions = set([x[0] for x in sure_tw_matches])
		sure_trg_positions = set([x[1] for x in sure_tw_matches])

		new_pos_pairs = pos_pairs
		for pair in pos_pairs:
			if pair[0] in sure_src_positions or pair[1] in sure_trg_positions:
				new_pos_pairs.remove(pair)
		for matches in sure_tw_matches:
			new_pos_pairs.append(matches)

		
		final_complete_pos_pairs.append(new_pos_pairs)
		# break







################### code for translation words  ###################
################### ends here	                ###################






############# code portion write out puts to ################
############# file & to seperately output    ################
############# the titus alignments to use it ################
############# for evaluation                 ################

temp = final_complete_pos_pairs
final_complete_pos_pairs = []
if NT:
	lid = 23146
else:
	lid = 1
for row in temp:
	final_complete_pos_pairs.append([lid,lid,row,"False"])
	lid=lid+1

pkl_file = open(output_pickle_file_name,"wb")
pickle.dump(final_complete_pos_pairs,pkl_file)
pkl_file.close()

for num,verse in enumerate(final_complete_pos_pairs):
	outfile.write(str(verse[0])+","+str(verse[1])+",")
	for align in verse[2]:
		# if num >= 6747 and num <6793:
			# evalfile.write(str(num+1)+" "+str(align[0])+" "+str(align[1])+"\n")
		outfile.write(str(align[0])+"-"+str(align[1])+" ")
	outfile.write(","+verse[3]+"\n")
outfile.close()
# evalfile.close()


############# output write code ends here    ################
