#!/bin/bash

DATE=$1
TWITTER_DATA_PATH=$2

DB_RAWDATA=salt_rawdata_${DATE}
DB_COL_RAWDATA=SALT_DB_${DATE}

RAWDATA_DIR=./rawdata/
RAWDATA_FILE_PATH=${RAWDATA_DIR}raw_${DATE}
VOCA_DIR=./voca/
VOCA_FILE_PATH=${VOCA_DIR}voca_${DATE}
MTX_DIR=./mtx/${DATE}/
NEIGHBOR_MTX_DIR=./mtx_neighbor/${DATE}/
TOPICS_DIR=./topics/${DATE}/

START=$(date +%s);

if [ -z ${DATE} ]; 
then
	echo "Usage: bash one_shot.sh [date or date_interval(IN)] [rawdata_path(IN, optional)]"
	echo "For example, bash one_shot.sh 130910 or bash one_shot.sh 131103-131105"
	exit 1
fi

if [ -z != ${TWITTER_DATA_PATH} ];
then
	echo "python mongoimport.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${TWITTER_DATA_PATH}"
	python mongoimport.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${TWITTER_DATA_PATH}

	echo "python export_rawdata.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${RAWDATA_FILE_PATH}"
	python export_rawdata.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${RAWDATA_FILE_PATH}
fi

echo "python create_voca.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${VOCA_FILE_PATH}"
python create_voca.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${VOCA_FILE_PATH}

echo "python termdoc_gen_atonce.py ${VOCA_FILE_PATH} ${DB_RAWDATA} ${DB_COL_RAWDATA} ${MTX_DIR}"
python termdoc_gen_atonce.py ${VOCA_FILE_PATH} ${DB_RAWDATA} ${DB_COL_RAWDATA} ${MTX_DIR}

echo "python termdoc_gen_neighbor.py ${MTX_DIR} ${NEIGHBOR_MTX_DIR}"
python termdoc_gen_neighbor.py ${MTX_DIR} ${NEIGHBOR_MTX_DIR}

echo "python topic_modeling_module_all.py ${NEIGHBOR_MTX_DIR} ${VOCA_FILE_PATH} ${TOPICS_DIR}"
python topic_modeling_module_all.py ${NEIGHBOR_MTX_DIR} ${VOCA_FILE_PATH} ${TOPICS_DIR}

END=$(date +%s);

echo $((END-START)) | awk '{print "Done. Elapsed time: " int($1/60)"m "int($1%60)"s"}'