#!/bin/bash

python db_gen.py mx960_1/
python db_gen.py mx960_2/
python db_gen.py mx960_3/
python db_gen.py mx960_5/
python db_gen.py mx2010/
# python db_gen.py ptx1/
# python db_gen.py ptx2/

cp mx960_1/db.json ./databases/mx960/mx960_1.json
cp mx960_2/db.json ./databases/mx960/mx960_2.json
cp mx960_3/db.json ./databases/mx960/mx960_3.json
cp mx960_5/db.json ./databases/mx960/mx960_5.json
cp mx2010/db.json ./databases/mx2010/mx2010.json
# cp ptx1/db.json ../bpjuniper/model/sim/databases/ptx/ptx1.json
# cp ptx2/db.json ../bpjuniper/model/sim/databases/ptx/ptx2.json
