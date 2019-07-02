import pymysql,codecs,sys

host="localhost"    # your host, usually localhost
user="root"         # your username
password="password"  # your password
database="AutographaMT_Staging"

# host="159.89.167.64"    # your host, usually localhost
# user="test_user"         # your username
# password="staging&2414"  # your password
# database="AutographaMTStaging"


query = '''select map.Book, map.Chapter, map.Verse, wrd.Lid, wrd.Position, wrd.Word, align.LidTrg, align.PositionTrg, align.Strongs 
from {} as wrd 
right join {} as align on wrd.Lid=align.LidSrc and wrd.Position=align.PositionSrc
join Bcv_LidMap as map on wrd.Lid=map.ID 
order by Lid, Position;'''



def export(conn,word_table,alignment_table):
	cur = conn.cursor()
	dynamic_query = query.format(word_table,alignment_table)
	cur.execute(dynamic_query)
	# print(query_result)

	next_row = cur.fetchone()
	prev_lid = None


	output_string = "Book\tBook Number\tChapter\tVerse Number\tVerse Text\n"
	verse_buffer = []
	while(next_row):
		LidSrc = next_row[3]
		LidTrg = next_row[6]
		if LidSrc != LidTrg:
			print('SKIPPING an alignment: Across Verses')
			next_row = cur.fetchone()
			continue


		Book = next_row[0]
		Chapter = next_row[1]
		Verse = next_row[2]
		PositionSrc = next_row[4]
		WordSrc = next_row[5]
		Strongs = next_row[8]
		PositionTrg = next_row[7] 

		if LidSrc == prev_lid:
			verse_buffer.append((WordSrc,Strongs))
		else:
			if len(verse_buffer) > 0:
				row = str(prev_Book)+"\t"+bookmap[prev_Book][0]+"\t"+str(prev_Chapter)+"\t"+str(prev_verse)+"\t"
				for word in verse_buffer:
					row += word[0]+"<"+str(word[1])+"> "
				output_string += row+"\n"
				# file.write(row+"\n")
				# print(Book)
				# # if Book == 42:
				# 	break
			prev_lid = LidSrc
			prev_Book = Book
			prev_Chapter = Chapter
			prev_verse = Verse
			verse_buffer = []
		next_row = cur.fetchone()
	# file.close()
	return output_string

bookmap = {
1 : ("Genesis", "GEN"),
2 : ("Exodus ", "EXO"),
3 : ("Leviticus  ", "LEV"),
4 : ("Numbers", "NUM"),
5 : ("Deuteronomy", "DEU"),
6 : ("Joshua ", "JOS"),
7 : ("Judges ", "JDG"),
8 : ("Ruth   ", "RUT"),
9 : ("1 Samuel   ", "1SA"),
10 : ("2 Samuel   ", "2SA"),
11 : ("1 Kings", "1KI"),
12 : ("2 Kings", "2KI"),
13 : ("1 Chronicles   ", "1CH"),
14 : ("2 Chronicles   ", "2CH"),
15 : ("Ezra   ", "EZR"),
16 : ("Nehemiah   ", "NEH"),
17 : ("Esther ", "EST"),
18 : ("Job", "JOB"),
19 : ("Psalms ", "PSA"),
20 : ("Proverbs   ", "PRO"),
21 : ("Ecclesiastes   ", "ECC"),
22 : ("Song of Solomon", "SNG"),
23 : ("Isaiah ", "ISA"),
24 : ("Jeremiah   ", "JER"),
25 : ("Lamentations   ", "LAM"),
26 : ("Ezekiel", "EZK"),
27 : ("Daniel ", "DAN"),
28 : ("Hosea  ", "HOS"),
29 : ("Joel   ", "JOL"),
30 : ("Amos   ", "AMO"),
31 : ("Obadiah", "OBA"),
32 : ("Jonah  ", "JON"),
33 : ("Micah  ", "MIC"),
34 : ("Nahum  ", "NAM"),
35 : ("Habakkuk   ", "HAB"),
36 : ("Zephaniah  ", "ZEP"),
37 : ("Haggai ", "HAG"),
38 : ("Zechariah  ", "ZEC"),
39 : ("Malachi", "MAL"),
40 : ("Matthew", "MAT"),
41 : ("Mark   ", "MRK"),
42 : ("Luke   ", "LUK"),
43 : ("John   ", "JHN"),
44 : ("Acts   ", "ACT"),
45 : ("Romans ", "ROM"),
46 : ("1 Corinthians  ", "1CO"),
47 : ("2 Corinthians  ", "2CO"),
48 : ("Galatians  ", "GAL"),
49 : ("Ephesians  ", "EPH"),
50 : ("Philippians", "PHP"),
51 : ("Colossians ", "COL"),
52 : ("1 Thessalonians", "1TH"),
53 : ("2 Thessalonians", "2TH"),
54 : ("1 Timothy  ", "1TI"),
55 : ("2 Timothy  ", "2TI"),
56 : ("Titus  ", "TIT"),
57 : ("Philemon   ", "PHM"),
58 : ("Hebrews", "HEB"),
59 : ("James  ", "JAS"),
60 : ("1 Peter", "1PE"),
61 : ("2 Peter", "2PE"),
62 : ("1 John ", "1JN"),
63 : ("2 John ", "2JN"),
64 : ("3 John ", "3JN"),
65 : ("Jude   ", "JUD"),
66 : ("Revelation ", "REV")}


if __name__ == '__main__':
	if len(sys.argv) != 4:
		print("USAGE EXAMPLE:\n python export_strong_embbed_bible.py Hin_4_BibleWord Hin_4_Grk_UGNT4_Alignment Hindi_StrongsNT.tsv")
		print("SET THE DB CREDENTIALS IN CODE")
		sys.exit(1)

	word_table = sys.argv[1]
	alignment_table = sys.argv[2]
	outfile = sys.argv[3]


	db = pymysql.connect(host=host,   
		                     user=user, 
		                     password=password, 
		                     database=database,
		                     charset='utf8mb4')
		                     # port=port)
	

	output_string = export(db, word_table, alignment_table)
	db.close()

	file  = codecs.open(outfile,mode='w',encoding='utf-8')
	file.write(output_string)
	file.close()
