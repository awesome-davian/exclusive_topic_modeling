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

def checkInputValidation(method, contents):

    # just print the information at this moment.

    error_code = 200;

    if method == 'GET_TOPICS':
        # logging the requested items

        terms = contents['terms'];
        include_keywords = terms['include'];
        exclude_keywords = terms['exclude'];

        for word in include_keywords:
            logging.debug('include keyword: %s', word);
        for word in exclude_keywords:
            logging.debug('exclude keyword: %s', word);

        tiles = contents['tiles'];
        for tile in tiles:
            logging.debug('x: %s, y: %s, level: %s', tile['x'], tile['y'], tile['level']);

    return error_code;

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

    contents = request.get_json(silent=True);

    logging.debug('contents: %s', contents);

    res = checkInputValidation('GET_TOPICS', contents);
    if  res != 200:
        return 'error'

    terms = contents['terms'];
    include_keywords = terms['include'];
    exclude_keywords = terms['exclude'];

    tiles = contents['tiles'];
    
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

@app.route('/GET_WORD_REF_COUNT', methods=['POST'])
def request_get_word_ref_count():

    contents = request.get_json(silent=True);

    logging.debug('contents: %s', contents);

    res = checkInputValidation('GET_WORD_REF_COUNT', contents);
    if  res != 200:
        return 'error'

    word = contents['word'];
    tiles = contents['tiles'];
    
    # run topic modeling for each tile
    counts = [];
    for tile in tiles:
        level = tile['level'];
        x = tile['x']
        y = tile['y']

        # these parameters are set by another function such as a set_params. 
        # we use the predefined value at this moment.
        time_range = {};
        time_range['start_date'] = 0;
        time_range['end_date'] = 0;

        count = TM.get_word_ref_count(level, x, y, word);
        counts.append(count);

    # verify that the calculation is correct using log.
    for count in counts:
        logging.debug('count: %s', count)

    json_data = json.dumps(counts);

    return json_data;

@app.route('/GET_DOCS_INCLUDING_WORD', methods=['POST'])
def request_get_docs_including_word():

    contents = request.get_json(silent=True);

    logging.debug('contents: %s', contents);

    res = checkInputValidation('GET_DOCS_INCLUDING_WORD', contents);
    if  res != 200:
        return 'error'

    word = contents['word'];
    tiles = contents['tiles'];
    
    # run topic modeling for each tile
    docs = [];
    for tile in tiles:
        level = tile['level'];
        x = tile['x']
        y = tile['y']

        # these parameters are set by another function such as a set_params. 
        # we use the predefined value at this moment.
        time_range = {};
        time_range['start_date'] = 0;
        time_range['end_date'] = 0;

        docs_per_tile = TM.get_docs_including_word(level, x, y, word);
        docs.append(docs_per_tile);

    # verify that the calculation is correct using log.
    for docs_per_tile in docs:
        logging.debug('docs_per_tile: %s', docs_per_tile)

    json_data = json.dumps(counts);

    return json_data;

@app.route('/GET_WORD_INFO', methods=['POST'])
def request_get_word_info():

    # TBD
    
    return ;

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

    app.run(host='0.0.0.0', port='5000')
