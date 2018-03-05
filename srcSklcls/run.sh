python estimatePs_smldata.py ../ni_data/

python getbtySkl.py 01
python getbtySkl.py 02
python getbtySkl.py 03

python getEventSegPair.py 01
python getEventSegPair.py 02
python getEventSegPair.py 03

python getEvent.py 01
python getEvent.py 02
python getEvent.py 03

python statisticFrmOfSeg.py 01 ../ni_data/eventskl01
python statisticFrmOfSeg.py 02 ../ni_data/eventskl02
python statisticFrmOfSeg.py 03 ../ni_data/eventskl03

python getfrmofsegEvent.py 01 ../ni_data/frmOfele01
python getfrmofsegEvent.py 02 ../ni_data/frmOfele02
python getfrmofsegEvent.py 03 ../ni_data/frmOfele03
