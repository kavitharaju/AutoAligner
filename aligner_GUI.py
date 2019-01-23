from tkinter import *
from tkinter import messagebox,filedialog
import subprocess,shlex
import csv, codecs, sys

sys.path.append('./Scripts')
from Names_occurences import names_ref_list


langs = ['asm','eng','ben','guj','grk','hin','kan','mal','mar','odi','pun','tam','tel','urd']

def call_bash_script(src,src_inp,trg,trg_inp,out_table,sw,stm,ne,tool,tw,prn):
	inpt = str(src.get())+' - '+str(trg.get())+' - '+str(sw.get())+' - '+str(stm.get())+' - '+str(ne.get())+' - '+str(tool.get())+' - '+str(tw.get())+' - '+str(prn.get())+' - '+str(src_inp.get())+' - '+str(trg_inp.get())
	if src.get() == '--select--' or src_inp.get()=='' or trg.get()=='--select--' or trg_inp.get()=='' or tool.get()==0 or out_table.get()=='':
		messagebox.showwarning("Missing Info", 'Source, Source table, Target, Target table, one tool and Output table are mandatory')
		return

	command = './auto_align.sh '+src.get()+' '+src_inp.get()+' '+trg.get()+' '+trg_inp.get()+' '+out_table.get()+' '

	if sw.get() :
		command += '- sw '
	if stm.get():
		command += '-stm '
	if ne.get():
		command += '-ne '
	if tool.get() ==1:
		command += '-giza '
	elif tool.get() ==2:
		command += '-fa '
	elif tool.get() == 3:
		command += '-ef '
	if tw.get():
		command += '-tw '
	if prn.get():
		command += '-prn'
	args = shlex.split(command)
	failed = subprocess.check_call([ 'bash']+ args)
	if failed:
		messagebox.showwarning("Alignment Info",'Alignment NOT completed successfully. See last_run_log.txt for details')
	else:
		messagebox.showinfo('Alignment into','Alignment done and added to DB!')


def see_how_to_add(resouce):
	resouce = resouce.get()
	print(resouce)
	if resouce==0:
		messagebox.showwarning('Add Resources','Select a resouce to see how to add it')
	if resouce==1:
		messagebox.showinfo('Add Resources','Fill the \n\nResources/Stopwords.csv \n\nfile(on excel/calc), \nSave and close.\nThen press the Load buton on this window')
	if resouce==2:
		messagebox.showinfo('Add Resources','Fill the \n\nResources/Names.csv \n\nfile(on excel/calc), \nSave and close.\nThen press the Load buton on this window')
	if resouce==3:
		messagebox.showinfo('Add Resources','Fill the \n\nResources/TranslationWords.csv \n\nfile(on excel/calc), \nSave and close.\nThen press the Load buton on this window')
	if resouce==4:
		messagebox.showinfo('Add Resources','Fill the \n\nResources/Pronouns.csv \n\nfile(on excel/calc), \nSave and close.\nThen press the Load buton on this window')

def add_resource(res_choice):
	resouce = res_choice.get()
	if resouce==0:
		messagebox.showwarning('Add Resources','Select a resouce \nand update the corresponding file\n(see "how to?"), \nto load it')
	if resouce==1:
		reload_stopwords()	
	if resouce==2:
		reload_names()
	if resouce==3:
		reload_tws()
	if resouce==4:
		reload_pronouns()


def reload_stopwords():
	infile = 'Resources/Stopwords.csv'

	outfile = codecs.open('Scripts/stopword_lookup.py',mode='w',encoding='utf8')


	col_list = ["asm_stopwords","ben_stopwords","guj_stopwords","hin_stopwords","kan_stopwords","mal_stopwords","mar_stopwords","pun_stopwords","odi_stopwords","tam_stopwords","tel_stopwords","urd_stopwords","grk_stopwords","eng_stopwords"]

	for index,col in enumerate(col_list):
		outfile.write(col+" = [")
		with open(infile) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter='\t')
			next(csv_reader,None)

			for row in csv_reader:
				if row[index]!='':
					outfile.write('"'+row[index]+'", ')
		outfile.write(']\n\n')
	outfile.close()
	messagebox.showinfo('Add Resources','Stopwords refreshed!')


def reload_names():
	infile = 'Resources/Names.csv'

	outfile = codecs.open('Scripts/name_lookup.py',mode='w',encoding='utf8')


	col_list = ["grk_names", "eng_names", "ref_names", "asm_names", "ben_names", "guj_names", "kan_names", "mal_names", "hin_names", "mar_names", "pun_names", "odi_names", "tam_names", "tel_names", "urd_names"]

	for index,col in enumerate(col_list):
		outfile.write(col+" = [")
		with open(infile) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter='\t')
			next(csv_reader,None)

			for row in csv_reader:
				if row[index]!='':
					outfile.write('"'+row[index]+'", ')
		outfile.write(']\n\n')
	outfile.write('names_ref_list ='+str(names_ref_list)+'\n\n')
	outfile.close()
	messagebox.showinfo('Add Resources','Names refreshed!')

def reload_tws():
	infile = 'Resources/TranslationWords.csv'

	outfile = codecs.open('Scripts/tw_lookup.py',mode='w',encoding='utf8')


	col_list = ["grk_tws", "eng_tws", "asm_tws", "ben_tws", "guj_tws", "hin_tws", "kan_tws", "mal_tws", "mar_tws", "pun_tws", "odi_tws", "tam_tws", "tel_tws", "urd_tws"]

	for index,col in enumerate(col_list):
		outfile.write(col+" = [")
		with open(infile) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter='\t')
			next(csv_reader,None)

			for row in csv_reader:
				if row[index]!='':
					str_list = row[index].split(',')
					outfile.write(str(str_list)+',\n')
		outfile.write(']\n\n')
	outfile.close()
	messagebox.showinfo('Add Resources','Translation Words refreshed!')

def reload_pronouns():
	infile = 'Resources/Pronouns.csv'

	outfile = codecs.open('Scripts/pronoun_lookup.py',mode='w',encoding='utf8')


	col_list = ["grk_pronouns", "eng_pronouns", "asm_pronouns", "ben_pronouns", "guj_pronouns", "hin_pronouns", "kan_pronouns", "mal_pronouns", "mar_pronouns", "pun_pronouns", "odi_pronouns", "tam_pronouns", "tel_pronouns", "urd_pronouns"]

	for index,col in enumerate(col_list):
		outfile.write(col+" = [")
		with open(infile) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter='\t')
			next(csv_reader,None)

			for row in csv_reader:
				if row[index]!='':
					str_list = row[index].split(',')
					outfile.write(str(str_list)+',\n')
		outfile.write(']\n\n')
	outfile.close()
	messagebox.showinfo('Add Resources','Pronouns refreshed!')






def launch_gui():
	global srctable,trgtable
	m=Tk()
	m.title('The Interlinear- Auto Aligner')
	m.minsize(550,300)
	m.pack_propagate(0)

	align_frame = Frame(m,highlightbackground="black", highlightcolor="black", highlightthickness=1, bd= 0)
	align_frame.grid(row=0,column=0,padx=10,pady=10)

	# Language frame
	lang_frame = Frame(align_frame)
	lang_frame.grid(column=1,row=0, sticky=(N,W,E,S),pady=30)

	defaultSrc = StringVar(m)
	defaultSrc.set('--select--')
	Label(lang_frame,text='Source').grid(row=0,column=1)
	src_list = OptionMenu(lang_frame, defaultSrc, *langs)
	src_list.config(width=10)
	src_list.grid(row=1,column=1)

	p1 = Label(lang_frame,text='Tablename')
	p1.grid(row=2,column=1)
	srctable = StringVar(m)
	Entry(lang_frame,textvariable=srctable).grid(row=3,column=1)


	p2 = Label(lang_frame,text='Tablename')
	p2.grid(row=2,column=2)
	trgtable = StringVar(m)
	Entry(lang_frame,textvariable=trgtable).grid(row=3,column=2)

	defaultTrg = StringVar(m)
	defaultTrg.set('--select--')
	Label(lang_frame,text='Target').grid(row=0,column=2)
	trg_list = OptionMenu(lang_frame, defaultTrg, *langs)
	trg_list.config(width=10)
	trg_list.grid(row=1,column=2)




	# Preprocessing frame

	prepro_frame = Frame(align_frame)
	prepro_frame.grid(column=0,row=1, sticky=(N,W,E,S))

	l1 = Label(prepro_frame,text='Preprocessing')
	l1.configure(font=('Helvetica',11,'bold'))
	l1.grid(row=0,rowspan=2)

	prepro1 = IntVar()
	Checkbutton(prepro_frame, text='Stopword removal', variable=prepro1).grid(row=2, sticky=W)
	prepro2 = IntVar()
	Checkbutton(prepro_frame, text='Stemming', variable=prepro2).grid(row=3, sticky=W)
	prepro3 = IntVar()
	Checkbutton(prepro_frame, text='Names removal', variable=prepro3).grid(row=4, sticky=W)


	# tool frame

	tool_frame = Frame(align_frame)
	tool_frame.grid(column=1,row=1,columnspan=2)
	l2 = Label(tool_frame,text='Tool')
	l2.configure(font=('Helvetica',11,'bold'))
	l2.grid(row=0,rowspan=2)
	tool = IntVar()
	Radiobutton(tool_frame, text='GIZA        ', variable=tool, value=1).grid(row=2)
	Radiobutton(tool_frame, text='FastAlign', variable=tool, value=2).grid(row=3)
	Radiobutton(tool_frame, text='Efmaral   ', variable=tool, value=3).grid(row=4)



	# Postprocessing frame

	postpro_frame = Frame(align_frame)
	postpro_frame.grid(column=3,row=1, sticky=(N,W,E,S))

	l3 = Label(postpro_frame,text='Postprocessing: \nImport pre-aligned words')
	l3.configure(font=('Helvetica',11,'bold'))
	l3.grid(row=0,rowspan=2)

	postpro1 = IntVar()
	Checkbutton(postpro_frame, text='Translation words', variable=postpro1).grid(row=2, sticky=W)
	postpro2 = IntVar()
	Checkbutton(postpro_frame, text='Pronouns', variable=postpro2).grid(row=3, sticky=W)

	# Action frame
	
	action_frame = Frame(align_frame)
	action_frame.grid(columnspan=4,pady=50)

	Label(action_frame,text='Output Table').grid(row=0,column=0)
	out_table = StringVar(m)
	Entry(action_frame,textvariable=out_table).grid(row=0,column=1)

	button = Button(action_frame, text='Align', command=lambda: call_bash_script(defaultSrc,srctable,defaultTrg,trgtable,out_table,prepro1,prepro2,prepro3,tool,postpro1,postpro2))
	button.grid(row=2,columnspan=2,pady=10)


	# Resources Frame

	res_frame = Frame(m,highlightbackground="black", highlightcolor="black", highlightthickness=1, bd= 0)
	res_frame.grid(row=0, column=1, rowspan=3, pady=10, padx=10)

	l4 = Label(res_frame,text='Add Resources')
	l4.configure(font=('Helvetica',11,'bold'))
	l4.grid(row=0,pady=10,padx=10)



	res_choice = IntVar(m)
	Radiobutton(res_frame, text='Stopwords', variable=res_choice, value=1).grid(row=3,sticky=W)
	Radiobutton(res_frame, text='Names', variable=res_choice, value=2).grid(row=4,sticky=W)
	Radiobutton(res_frame, text='Translation Words ', variable=res_choice, value=3).grid(row=5,sticky=W)
	Radiobutton(res_frame, text='Pronouns ', variable=res_choice, value=4).grid(row=6,sticky=W)

	Button(res_frame,text='How to?',font=('Helvetica',8),command=lambda : see_how_to_add(res_choice)).grid(row=7,sticky=W,pady=10,padx=10)

	Button(res_frame,text='Load',font=('Helvetica',11,'bold'),command=lambda : add_resource(res_choice)).grid(row=8)



	m.mainloop()



if __name__ == '__main__':
	launch_gui()