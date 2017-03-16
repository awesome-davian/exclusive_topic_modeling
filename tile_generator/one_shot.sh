#!/bin/bash

DATE=$1
TWITTER_DATA_PATH=$2

DB_RAWDATA=salt_rawdata_${DATE}
DB_COL_RAWDATA=SALT_DB_${DATE}

RAWDATA_DIR=./data/rawdata/
RAWDATA_FILE_PATH=${RAWDATA_DIR}raw_${DATE}
VOCA_DIR=./data/voca/
VOCA_FILE_PATH=${VOCA_DIR}voca_${DATE}
MTX_DIR=./data/mtx/${DATE}/
# NEIGHBOR_MTX_DIR=./data/mtx_neighbor/${DATE}/
TOPICS_DIR=./data/topics/${DATE}/

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
	echo "python export_rawdata.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${RAWDATA_FILE_PATH}"
	python export_rawdata.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${RAWDATA_FILE_PATH}
else
	echo ""
	echo "Do not import rawdata because the argv[2](rawdata path) is not exist."
fi

echo ""
echo "python create_voca.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${VOCA_FILE_PATH}"
python create_voca.py ${DB_RAWDATA} ${DB_COL_RAWDATA} ${VOCA_FILE_PATH}

echo ""
echo "python termdoc_gen_atonce.py ${VOCA_FILE_PATH} ${DB_RAWDATA} ${DB_COL_RAWDATA} ${MTX_DIR}"
python termdoc_gen_atonce.py ${VOCA_FILE_PATH} ${DB_RAWDATA} ${DB_COL_RAWDATA} ${MTX_DIR}

# echo ""
# echo "python termdoc_gen_neighbor.py ${MTX_DIR} ${NEIGHBOR_MTX_DIR}"
# python termdoc_gen_neighbor.py ${MTX_DIR} ${NEIGHBOR_MTX_DIR}

echo ""
echo "python topic_modeling_module_all.py ${MTX_DIR} ${VOCA_FILE_PATH} ${TOPICS_DIR}"
python topic_modeling_module_all.py ${MTX_DIR} ${VOCA_FILE_PATH} ${TOPICS_DIR}

END=$(date +%s);

echo ""
echo $((END-START)) | awk '{print "Done. Total Elapsed time: " int($1/60)"m "int($1%60)"s"}'