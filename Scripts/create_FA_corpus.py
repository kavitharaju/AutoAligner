import codecs,sys

if(len(sys.argv)==5):
	src = sys.argv[1]
	trg = sys.argv[2]

	src_path = sys.argv[3]
	trg_path = sys.argv[4]
else:
	print("Usage: python3 create_FA_corpus.py src trg src_path trg_path"+
		"\n src and trg are 3-letter language codes"+
		"\n src_path and trg_path are path to cleaned and tokenized bible files, one verse per line.")
	sys.exit(0)



cleaned_src = codecs.open(src_path,mode="r",encoding="utf-8").readlines()
cleaned_trg = codecs.open(trg_path,mode="r",encoding="utf-8").readlines()


pc_fa = codecs.open("../Resources/"+src+"."+trg+".parallel_corpus_FAformat.txt",mode="w",encoding="utf-8")
i=23146
for m,g in zip(cleaned_src,cleaned_trg):
	m=m.replace("\n","")
	g=g.replace("\n","")
	m_str = "".join(m)
	g_str = "".join(g)
	# pc_fa.write("<s snum="+str(i)+">"+m_str.strip()+"</s> ||| <s snum="+str(i)+">"+g_str.strip()+"</s>\n")
	pc_fa.write(m_str.strip()+" ||| "+g_str.strip()+"\n")
	i = i+1
pc_fa.close()






