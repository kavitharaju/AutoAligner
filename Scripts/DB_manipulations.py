import pymysql,codecs,sys,pickle

host="localhost"    # your host, usually localhost
user="root"         # your username
password="password"  # your password
database="AutographaMT_Staging"

db = pymysql.connect(host=host,   
	                     user=user, 
	                     password=password, 
	                     database=database,
	                     charset='utf8mb4')


def read_verses(tablename,file,Strongs=False):
	cur = db.cursor()

	if Strongs:
		read_verses_query_for_grk = '''select LID, group_concat(Strongs ORDER BY Position SEPARATOR ' ') from '''+tablename+''' where LID is not NULL Group by LID order by LID '''
		cur.execute(read_verses_query_for_grk)
	else:
		read_verses_query = '''select LID, group_concat(Word ORDER BY Position SEPARATOR ' ') from '''+tablename+''' where LID is not NULL Group by LID order by LID '''
		cur.execute(read_verses_query)
	verse_list = cur.fetchall()

	outfile = codecs.open(file,mode='w',encoding='utf-8')

	lid_tracker = verse_list[0][0]
	for lid,verse in verse_list:
		while (lid_tracker< lid):
			outfile.write('\n')
			lid_tracker +=1
		outfile.write(verse)
	outfile.close()
	print('Bible text read to '+file)

def write_alignment(srctablename,trgtablename,alignmnenttablename,pickle_file):
	cur = db.cursor()

	cur.execute('''show tables like "'''+alignmnenttablename+'''"''')
	if len(cur.fetchall()) == 0:
		create_alignmenttable_query  = '''create table '''+alignmnenttablename+''' like Hin_4_Grk_UGNT4_Alignment'''
		cur.execute(create_alignmenttable_query)
		db.commit()
	cur.execute('''truncate '''+alignmnenttablename)
	db.commit()

	alignments = pickle.load(open(pickle_file,"rb"))

	select_src_words_query = '''select Word from '''+srctablename+''' where LID=%s ORDER BY Position'''
	select_trg_words_query = '''select Strongs from '''+trgtablename+''' where LID=%s ORDER BY Position'''
	insert_pos_pair_query ='''insert into '''+alignmnenttablename+'''(LidSrc, LidTrg, PositionSrc,PositionTrg,WordSrc,Strongs,UserId,Stage,Type) values(%s,%s,%s,%s,%s,%s,0,0,0)'''
	for verse in alignments:
		src_lid = verse[0]
		trg_lid = verse[1]
		pos_pairs = verse[2]

		cur.execute(select_src_words_query,(src_lid))
		src_words = cur.fetchall()
		cur.execute(select_trg_words_query,(trg_lid))
		trg_words = cur.fetchall()

		if len(src_words)==0 or len(trg_words)==0:
			continue

		for pair in pos_pairs: 
			src_pos = pair[0]
			trg_pos = pair[1]
			try:
				if src_pos==255:
					src_word = None
				else:
					src_word = src_words[src_pos]
				if trg_pos == 255:
					trg_strongs = None
				else:
					trg_strongs = trg_words[trg_pos]
				cur.execute(insert_pos_pair_query,(src_lid,trg_lid,src_pos,trg_pos,src_word,trg_strongs))
			except Exception as e:
				print('src_lid:'+str(src_lid))
				print('trg_lid:'+str(trg_lid))
				print('src_words:'+str(src_words))
				print('trg_words:'+str(trg_words))
				print('pos_pairs:'+str(pos_pairs))
				print('src_pos:'+str(src_pos))
				print('trg_pos:'+str(trg_pos))
				

				raise e
	db.commit()



if __name__ == '__main__':
	Strongs = False
	cmd_line_params = sys.argv
	if cmd_line_params[1] == 'read' and len(cmd_line_params) >= 4:
		tablename = cmd_line_params[2]
		filename = cmd_line_params[3]
		if len(cmd_line_params)==5 and cmd_line_params[4] in ['-strongs','-Strongs','strongs','Strongs'] :
			Strongs=True
		read_verses(tablename,filename,Strongs)
	elif cmd_line_params[1] == 'write' and len(cmd_line_params) == 6:
		srctablename = cmd_line_params[2]
		trgtablename = cmd_line_params[3]

		tablename = cmd_line_params[4]
		tablename = tablename+"_test"
		pickle_file = cmd_line_params[5]
		write_alignment(srctablename,trgtablename, tablename,pickle_file)
	else:
		print('USAGE: \npython3 DB_manipulation.py read input_tablename output_filename [-strongs]\n Example: python3 DB_manipulation.py read Hin_4_BibleWord ../Resouces/hin_cleaned_bible.txt')
		print('\n\nOR\n\n')
		print('python3 DB_manipulation.py write input_tablename output_filename alignment_tablename input_picklefile (the target language should be grk )\n Example: python3 DB_manipulation.py write Hin_4_Grk_UGNT4_Alignment ../Models/hin.grk.sw.stm.ne.giza.tw..pkl')
		
		sys.exit(1)

	
