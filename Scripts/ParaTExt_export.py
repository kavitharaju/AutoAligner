import pymysql,codecs

# host="localhost"    # your host, usually localhost
# user="root"         # your username
# password="password"  # your password
# database="AutographaMT_Staging"

host="159.89.167.64"    # your host, usually localhost
user="test_user"         # your username
password="staging&2414"  # your password
database="AutographaMTStaging"





query = '''select Book, Chapter, Verse, LidSrc, PositionSrc, WordSrc, LidTrg, PositionTrg, Strongs 
from {} left join Bcv_LidMap on LidSrc=Bcv_LidMap.ID 
order by LidSrc, PositionSrc;'''

xml_header = '''<?xml version="1.0"?>

<Mappings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
'''
xml_footer = '''</Mappings>'''
xml_content_template = '''  <Mapping Reference="{}" Warning="false" Verified="false" Proposed="false" BeyondVerse="false">

    <SourceLinks>

      <SourceLink Word="{}" Strong="{}" Index="{}"></SourceLink>

    </SourceLinks>

    <TargetLinks>

      {}

    </TargetLinks>

  </Mapping>
'''

one_target_template = '''<TargetLink>{}</TargetLink>
      '''

def export(conn,table):
	cur = conn.cursor()
	dynamic_query = query.format(table)
	cur.execute(dynamic_query)
	# print(query_result)

	next_row = cur.fetchone()
	prev_lid = None
	prev_PositionSrc = None


	output_string = xml_header
	output_string_list = []
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

		index = 0
		if LidSrc!=prev_lid:
			prev_lid = LidSrc
			verse_buffer = [WordSrc]
		else:
			for w in verse_buffer:
				if w==WordSrc:
					index += 1
			if PositionSrc != prev_PositionSrc:
				verse_buffer.append(WordSrc)

		if not PositionTrg:
			next_row = cur.fetchone()
			continue

		Reference=str(Book).zfill(3)+str(Chapter).zfill(3)+str(Verse).zfill(3)+"00"
		Word=str(WordSrc)
		Strong="G"+str(Strongs).zfill(4)
		Index=str(index)
		TargetLink=str(Book).zfill(3)+str(Chapter).zfill(3)+str(Verse).zfill(3)+"00"+str(PositionTrg*2).zfill(3)
		if PositionSrc != prev_PositionSrc or LidSrc != prev_lid:
			prev_PositionSrc = PositionSrc
			target_string = ''
		else:
			output_string_list = output_string_list[:-1]
		
		target_string += one_target_template.format(TargetLink)
		filled_template = xml_content_template.format(Reference,Word,Strong,Index,target_string)

		output_string_list.append(filled_template)


		next_row = cur.fetchone()
		# break
	for strng in output_string_list:
		output_string += strng 
	output_string += xml_footer
	cur.close()
	return output_string



if __name__ == '__main__':
	db = pymysql.connect(host=host,   
		                     user=user, 
		                     password=password, 
		                     database=database,
		                     charset='utf8mb4')
	tablename = "Mal_4_Grk_UGNT4_Alignment"
	output_string = export(db,tablename)

	db.close()
	file='ParaTExt_export.xml'
	outfile = codecs.open(file,mode='w',encoding='utf-8')
	outfile.write(output_string)
	outfile.close()