#!/bin/bash

DATE=$1
TWITTER_DATA_PATH=$2

DB_RAWDATA=salt_rawdata_${DATE}
DB_COL_RAWDATA=SALT_DB_${DATE}

RAWDATA_DIR=./data/${DATE}/rawdata/
VOCA_DIR=./data/${DATE}/voca/
MTX_DIR=./data/${DATE}/mtx/
W_DIR=./data/${DATE}/w/
NEIGHBOR_MTX_DIR=./data/${DATE}/nmtx/
TOPICS_DIR=./data/${DATE}/topics/

START=$(date +%s);

if [ -z ${DATE} ]; 
then
	echo "Usage: bash one_shot.sh [date or date_interval(IN)] [rawdata_path(IN, optional)]"
	echo "For example, bash one_shot.sh 130910 or bash one_shot.sh 131103-131105"
	exit 1
fi

if [ -z != ${TWITTER_DATA_PATH} ];
then
	echo ""
	echo "python mongoimport.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${TWITTER_DATA_PATH}"
	python mongoimport.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${TWITTER_DATA_PATH}

	echo ""
	echo "python export_rawdata.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${RAWDATA_DIR}"
	python export_rawdata.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${RAWDATA_DIR}
else
	echo ""
	echo "Do not import rawdata because the argv[2](rawdata path) is not exist."
fi

echo ""
echo "python create_voca.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${VOCA_DIR}"
python create_voca.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${VOCA_DIR}

echo ""
echo "python termdoc_gen_atonce_par.py ${VOCA_DIR} ${DB_RAWDATA} ${DB_COL_RAWDATA} ${MTX_DIR}"
python termdoc_gen_atonce_par.py ${VOCA_DIR} ${DB_RAWDATA} ${DB_COL_RAWDATA} ${MTX_DIR} #--> multi thread with par

# python termdoc_gen_atonce.py ${VOCA_DIR} ${DB_RAWDATA} ${DB_COL_RAWDATA} ${MTX_DIR} #--> single thread

#-----------------------------------------------------------------------------------------
# New version

# initial version
# echo ""
# echo "python run_nmf_no_schedule.py"
# python run_nmf_no_schedule.py ${MTX_DIR} ${W_DIR}

# scheduled version
# echo ""
# echo "python run_nmf_scheduled.py"
# python run_nmf_scheduled.py ${MTX_DIR} ${W_DIR}

# pipelined version
# echo ""
# echo "python run_nmf_pipelined.py" ${MTX_DIR} ${W_DIR}
# python run_nmf_pipelined.py ${MTX_DIR} ${W_DIR}


#-----------------------------------------------------------------------------------------
# Previous version

# echo ""
# echo "python termdoc_gen_neighbor.py ${MTX_DIR} ${NEIGHBOR_MTX_DIR}"
# python termdoc_gen_neighbor.py ${MTX_DIR} ${NEIGHBOR_MTX_DIR}

# topic modeling 은 Matlab 에서 수행
# echo ""
# echo "python topic_modeling_module_all.py ${MTX_DIR} ${VOCA_DIR} ${TOPICS_DIR}"
# python topic_modeling_module_all.py ${MTX_DIR} ${VOCA_DIR} ${TOPICS_DIR}

END=$(date +%s);

echo ""
echo $((END-START)) | awk '{print "Done. Total Elapsed time: " int($1/60)"m "int($1%60)"s"}'
