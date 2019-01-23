import sys,re,pickle

if len(sys.argv)==2:
	in_file = sys.argv[1]




input_lines = open(in_file,"r").readlines()

out_pickle = open("../Models/partial_pos_pair.pkl","wb")

start_num = 1
pos_pair_obj=[]
for line in input_lines:
	pos_pairs = re.split("\s+",line.strip())
	for pair in pos_pairs:
		if pair == '':
			continue

		i= re.split("-",pair)[0]
		j= re.split("-",pair)[1]
		pos_pair_obj.append((start_num,int(i),int(j)))
	start_num=start_num+1
	# break
# print(pos_pair_obj[:50])
pickle.dump(pos_pair_obj,out_pickle)
out_pickle.close()