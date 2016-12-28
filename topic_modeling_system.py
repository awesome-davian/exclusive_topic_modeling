from flask import Flask, render_template, request, redirect
import tile_generator
import topic_modeling_module
import database_wrapper
import os, sys
import json
import logging, logging.config

logging.config.fileConfig('logging.conf')

app = Flask(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def initProject():


    logging.debug('initProject')

    return

@app.route('/')
@app.route('/index')
@app.route('/web_client_test')
def web_client_test():
	return render_template("simple_web_client.html")

@app.route('/tile_generator_test')
def tile_generator_test():
	return render_template("simple_tile_generator.html")

@app.route('/GET_TOPICS/<uuid>', methods=['POST'])
def request_get_topics(uuid):

    print "uuid: " + uuid

    contents = request.get_json(silent=True)

    print contents



    data = {
        "tile": {"x": 5, "y": 4, "level": 12}, 
        "topic": [{
            "score": 4.315,
            "words": [
                {"score": 1.23, "word": "food"}, 
                {"score": 0.9855, "word": "burger"}, 
                {"score": 0.72735, "word": "fries"}, 
                {"score": 0.71, "word": "drinks"}
        ] }]
    }

    json_data = json.dumps(data)

    return json_data

    # zoom_level = 9
    # tile_id = 100
    # num_clusters = 3
    # num_keywords = 3
    # include_word_list = ""
    # exclude_word_list = ""
    # exclusiveness = 0
    # time_range = {}
    # time_range['start']=0
    # time_range['end']=0

    # sample parameters
    # zoom_level = request.args.get('zoom_level')
    # tile_id = request.args.get('tile_id')
    # num_clusters = request.args.get('num_clusters')
    # num_keywords = request.args.get('num_keywords')
    # include_word_list = request.args.get('include_word_list')
    # exclude_word_list = request.args.get('exclude_wor')
    # exclusiveness = request.args.get('zoom_level')
    # time_range = request.args.get('zoom_level')
    # time_range['start']=request.args.get('zoom_level')
    # time_range['end']=request.args.get('zoom_level')

    # TM.get_topics(zoom_level, tile_id, num_clusters, num_keywords, include_word_list, exclude_word_list, exclusiveness, time_range, 0)
    # return redirect('/web_client_test')

@app.route('/GET_WORD_REF_COUNT', methods=['GET'])
def request_get_word_ref_count():

    zoom_level = 9;
    tile_id = 100;
    keyword = "sample_word"

    TM.get_word_ref_count(zoom_level, tile_id, keyword);
    return redirect('/web_client_test')

@app.route('/GET_WORD_INFO', methods=['GET'])
def request_get_word_info():

    zoom_level = 9;
    tile_id = 100;
    keyword = "sample_word"

    TM.get_word_info(zoom_level, tile_id, keyword);
    return redirect('/web_client_test')

@app.route('/GENERATE_TILE', methods=['GET'])
def request_generate_tile():

    TG.make_default_tiles()
    return redirect('/tile_generator_test')

@app.route('/RUN_TOPIC_MODELING', methods=['GET'])
def request_run_topic_modeling():

    num_clusters = 3
    num_keywords = 3
    exclusiveness = 0

    TG.run_topic_modeling(TM, num_clusters, num_clusters, exclusiveness)
    return redirect('/tile_generator_test')

if __name__ == '__main__':

    initProject()

    DB = database_wrapper.DBWrapper()
    TM = topic_modeling_module.TopicModelingModule(DB)
    TG = tile_generator.TileGenerator(DB)

    app.run(host='0.0.0.0')
