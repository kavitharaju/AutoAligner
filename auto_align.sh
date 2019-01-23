# This Script intergrates the modules of the Auto Aligner
# Auto Aligner is meant to create the word alignments between two parallel Bibles(which are, versification corrected and added into the DB)
# The bible tables in the DB are expected to be of the following schema
# 		Field		Type
# 		-----		----
# 		LID			smallint(5) unsigned
# 		Position	tinyint(3) unsigned
# 		Word		varchar(30)
# It writes the output alignments back into the DB as positional pairs. The DB structure for the alignment table is
# 		Field			Type
# 		-----			----
# 		ID				int(11)
# 		LidSrc			smallint(5) unsigned
# 		LidTrg			smallint(5) unsigned
# 		PositionSrc		tinyint(3) unsigned
# 		PositionTrg		tinyint(3) unsigned
# 		Strongs			smallint(5) unsigned
# 		WordSrc			varchar(30)
# 		...
# to Run this script, command and parameters are:

# '''bash ./auto_align.sh src srctable trg trgtable outputtable [-sw] [-stm] [-ne] -tool [-tw] [-prn]'''

# src and trg are 3 letter language codes like hin, grk, mal, mar etc
# srctable and trgtable are corresponding BibleWord tables with schema describe above(former)
# outputtable is the alignment table with the latter schema
# the optional parameters select the processing steps; 
#       stopword removal, stemming, names removal(pre-alignment), translation word pre-alignment and pronoun pre-alignment respectively
# tool can take 3 values:
# 		-giza (for mgiza)
# 		-ef (for efmaral)
# 		-fa (for fastalign)


set -e

src=$1
srctable=$2
trg=$3
trgtable=$4
outputtable=$5

stopword=''
stemming=''
namedentity=''
giza=''
efmaral=''
fastalign=''
translationwords=''
pronouns=''


for param in "$@"
do 
if [ $param = "-sw" ]
then
stopword="-sw"
fi

if [ $param = "-stm" ]
then
stemming="-stm"
fi

if [ $param = "-ne" ]
then
namedentity="-ne"
fi

if [ $param = "-tw" ]
then
translationwords="-tw"
fi

if [ $param = "-prn" ]
then
pronouns="-prn"
fi 

if [ $param = "-giza" ]
then
giza='true'

fi 

if [ $param = "-ef" ]
then
efmaral='true'
fi 

if [ $param = "-fa" ]
then
fastalign='true'
fi 
done





cd Scripts
if [ "$src" = "grk" ]
then
echo "greek"
python3 DB_manipulations.py read $srctable ../Resources/$src_cleaned_bible.txt -strongs
else
echo "non-greek"
python3 DB_manipulations.py read $srctable ../Resources/$src_cleaned_bible.txt
fi
python3 Preprocessor.py $src ../Resources/$src_cleaned_bible.txt $stopword $stemming $namedentity
mv ../Models/preprocessed_bible.pkl ../Models/$src.preprocessed_bible.pkl
cp ../Resources/parallel_corpus_GIZAformat.txt ../Resources/$src.parallel_corpus_GIZAformat.txt

if [ "$trg" = "grk" ]
then

echo "greek"
python3 DB_manipulations.py read $trgtable ../Resources/$trg_cleaned_bible.txt -strongs
else
echo "non-greek"
python3 DB_manipulations.py read $trgtable ../Resources/$trg_cleaned_bible.txt
fi
python3 Preprocessor.py $trg ../Resources/$trg_cleaned_bible.txt $stopword $stemming $namedentity
mv ../Models/preprocessed_bible.pkl ../Models/$trg.preprocessed_bible.pkl
cp ../Resources/parallel_corpus_GIZAformat.txt ../Resources/$trg.parallel_corpus_GIZAformat.txt


cd ..

if [ "$giza" = "true" ]
then

cp Resources/$src.parallel_corpus_GIZAformat.txt Resources/corpus4giza/corp.tok.low.src
cp Resources/$trg.parallel_corpus_GIZAformat.txt Resources/corpus4giza/corp.tok.low.trg


cd AlignmentTools/symgiza-pp-master
./run.sh corp.tok.low.src corp.tok.low.trg ../../Resources/corpus4giza
cp ../../Resources/corpus4giza/data/out.A3.final_symal ../../Resources/$src.$trg.giza_sym.align

cd ../../Scripts

python tranlate_giza_out_to_positionalpair.py ../Resources/$src.$trg.giza_sym.align

python3 Postprocessor.py $src $trg $translationwords $pronouns -o ../Models/$src.$trg.$stopword.$stemming.$namedentity.giza.$translationwords.$pronouns.pkl

python3 DB_manipulations.py write $srctable $trgtable $outputtable ../Models/$src.$trg.$stopword.$stemming.$namedentity.giza.$translationwords.$pronouns.pkl 
cd ..



#perl src/wa_eval_align.pl res/titus_gold.wa res/titus_for_eval.wa
fi

if [ "$efmaral" = "true" ]
then

echo "Using efmaral"
cd Scripts
python3 create_FA_corpus.py $src $trg ../Resources/$src.parallel_corpus_GIZAformat.txt ../Resources/$trg.parallel_corpus_GIZAformat.txt
cd ..

cd AlignmentTools/efmaral-master

python3 align.py -i ../../Resources/$src.$trg.parallel_corpus_FAformat.txt > ../../Resources/forward.align

python3 align.py -r -i ../../Resources/$src.$trg.parallel_corpus_FAformat.txt > ../../Resources/reverse.align

cd ..
./fast_align-master/build/atools -i ../Resources/forward.align -j ../Resources/reverse.align -c grow-diag-final-and > ../Resources/sym.align.ef

cd ../Scripts
python3 translate_FAoutput_to_pospairs.py ../Resources/sym.align.ef


python3 Postprocessor.py $src $trg $translationwords $pronouns -o ../Models/$src.$trg.$stopword.$stemming.$namedentity.efmaral.$translationwords.$pronouns.pkl

python3 DB_manipulations.py write $srctable $trgtable $outputtable ../Models/$src.$trg.$stopword.$stemming.$namedentity.efmaral.$translationwords.$pronouns.pkl 
cd ..

#perl src/wa_eval_align.pl res/titus_gold.wa res/titus_for_eval.wa
fi


if [ "$fastalign" = "true" ]
then


echo "Using Fastalign"
cd Scripts
python3 create_FA_corpus.py $src $trg ../Resources/$src.parallel_corpus_GIZAformat.txt ../Resources/$trg.parallel_corpus_GIZAformat.txt
cd ..

./AlignmentTools/fast_align-master/build/fast_align -i Resources/$src.$trg.parallel_corpus_FAformat.txt -d -o > Resources/forward.align
./AlignmentTools/fast_align-master/build/fast_align -r -i Resources/$src.$trg.parallel_corpus_FAformat.txt -d -o > Resources/reverse.align
./AlignmentTools/fast_align-master/build/atools -i Resources/forward.align -j Resources/reverse.align -c grow-diag-final-and > Resources/sym.align.fa

cd Scripts
python3 translate_FAoutput_to_pospairs.py ../Resources/sym.align.fa

python3 Postprocessor.py $src $trg $translationwords $pronouns -o ../Models/$src.$trg.$stopword.$stemming.$namedentity.fastalign.$translationwords.$pronouns.pkl

python3 DB_manipulations.py write $srctable $trgtable $outputtable ../Models/$src.$trg.$stopword.$stemming.$namedentity.fastalign.$translationwords.$pronouns.pkl 
cd ..

#perl src/wa_eval_align.pl res/titus_gold.wa res/titus_for_eval.wa
fi

echo "finished aligning"

