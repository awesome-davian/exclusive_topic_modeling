from flask import Flask, render_template, request, redirect
import tile_generator
import topic_modeling_module
import database_wrapper
import os, sys
import json
import logging, logging.config
import constants

logging.config.fileConfig('logging.conf')

app = Flask(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def initProject():

    print('----- Topic Modeling System %s -----' % (constants.VERSION))

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

    logging.debug('uuid: %s', uuid);

    contents = request.get_json(silent=True);

    logging.debug('contents: %s', contents);

    terms = contents['terms'];
    include_keywords = terms['include'];
    exclude_keywords = terms['exclude'];

    tiles = contents['tiles'];

    # logging the requested items
    for word in include_keywords:
        logging.debug('include keyword: %s', word);
    for word in exclude_keywords:
        logging.debug('exclude keyword: %s', word);

    for tile in tiles:
        logging.debug('x: %s, y: %s, level: %s', tile['x'], tile['y'], tile['level']);
    
    # run topic modeling for each tile
    topics = [];
    for tile in tiles:
        zoom_level = tile['level'];
        x = tile['x']
        y = tile['y']

        # these parameters are set by another function such as a set_params. 
        # we use the predefined value at this moment.
        num_topics = constants.DEFAULT_NUM_TOPICS;         
        num_keywords = constants.DEFAULT_NUM_TOP_K;
        exclusiveness = constants.DEFAULT_EXCLUSIVENESS;
        time_range = {};
        time_range['start_date'] = 0;
        time_range['end_date'] = 0;
        topic = TM.get_topics(zoom_level, x, y, num_topics, num_keywords, include_keywords, exclude_keywords, exclusiveness, time_range);
        topics.append(topic);

    # verify that the calculation is correct using log.
    for topic in topics:
        logging.debug('topic: %s', topic)

    json_data = json.dumps(topics);

    return json_data;

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
    DB.connect("localhost", constants.DEFAULT_MONGODB_PORT)
    TM = topic_modeling_module.TopicModelingModule(DB)
    TG = tile_generator.TileGenerator(DB)

    app.run(host='0.0.0.0')
