import re,codecs,sys,pickle


filename = ""
if len(sys.argv)==2:
	filename = sys.argv[1]
else:
	print("Usage: python3 translate_giza_out_to_positionalpair.py giza_output_file")
	sys.exit(0)

giza_output = codecs.open("../Resources/"+filename,mode="r",encoding="utf-8")
positionalpair_output = codecs.open('../Models/'+filename+".partial_pos_pairs",mode="w",encoding="utf-8")
out_pickle = open("../Models/partial_pos_pair.pkl","wb")
start_num = 1


# pos_pair_pattern = re.compile("[\w\s]+{##}[\w\s]+{##}([\s\d-]+)",re.UNICODE)
pos_pair_pattern = re.compile(".+{##}.+{##}([\s\d-]+)",re.UNICODE)
num_pattern = re.compile("\d+",re.UNICODE)



line = giza_output.readline()
pos_pair_obj = []
while line:
	
	pos_pair_mth = re.search(pos_pair_pattern,line)
	
	if pos_pair_mth:
		pos_pair_str = pos_pair_mth.group(1)
		
		pos_pairs = re.split("\s+",pos_pair_str.strip())
		positionalpair_output.write(str(start_num)+",")
		
		for pair in pos_pairs:
			
			i= re.split("-",pair)[0]
			j= re.split("-",pair)[1]
			

			pos_pair_obj.append((start_num,int(i),int(j)))
			positionalpair_output.write(i+"-"+j+" ")
			# print(i+"-"+j)
	else:
		print("no match")
	start_num=start_num+1
	# break
	positionalpair_output.write("\n")

	line = giza_output.readline()

print(start_num)

giza_output.close()
positionalpair_output.close()
pickle.dump(pos_pair_obj,out_pickle)
out_pickle.close()