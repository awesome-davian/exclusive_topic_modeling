from flask import Flask, render_template, request, redirect
from flask_api import status
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

    error_string = "Success";

    if method == 'GET_TOPICS':

        parameters = [];
        exclusiveness = -1;
        topic_count = -1;
        word_count = -1;
        date = '0000-00-00'
        include_words = [];
        exclude_words = [];
        tiles = [];

        try: 
            parameters = contents['parameters']
            exclusiveness = parameters['exclusiveness'];
            topic_count = parameters['topic_count'];
            word_count = parameters['word_count'];
            date = parameters['date'];
            include_words = parameters['include_words'];
            exclude_words = parameters['exclude_words'];
            tiles = contents['tiles'];

        
            if exclusiveness < 0 or exclusiveness > 100:
                error_string = "Invalid exclusiveness.";
            if topic_count < 1 or topic_count > 10:
                error_string = "Invalid topic_count.";
            if word_count < 1 or word_count > 10:
                error_string = "Invalid word_count.";
            
            for tile in tiles:
                level = -1;
                x = -1;
                y = -1;

                level = tile['level'];
                x = tile['x']
                y = tile['y']
                
                if level < 9 or level > 13:
                    error_string = "Invalid tile.level";
                if x < 0:
                    error_string = "Invalid tile.x";
                if y < 0:
                    error_string = "Invalid tile.y";

        except KeyError as e:
            error_string = 'KeyError: ' + e.args[0];

        return error_string, parameters, exclusiveness, topic_count, word_count, date, include_words, exclude_words, tiles;

    elif method == 'GET_RELATED_DOCS':
        
        try:
            word = contents['word'];
            tile = contents['tile'];
            level = tile['level'];
            x = tile['x'];
            y = tile['y'];
            date = contents['date']

            if level < 9 or level > 13:
                error_string = "Invalid tile.level";
            if x < 0:
                error_string = "Invalid tile.x";
            if y < 0:
                error_string = "Invalid tile.y";

        except KeyError as e:
            error_string = 'KeyError: ' + e.args[0];
        
        return error_string, word, level, x, y, date;

    elif method == 'GET_HEATMAP':
        try:
            date_from = contents['parameters']['date']['from']
            date_to = contents['parameters']['date']['to']
            tiles = contents['tiles']
            for tile in tiles:
                level = -1;
                x = -1;
                y = -1;

                level = tile['level'];
                x = tile['x']
                y = tile['y']
                
                if level < 9 or level > 13:
                    error_string = "Invalid tile.level";
                if x < 0:
                    error_string = "Invalid tile.x";
                if y < 0:
                    error_string = "Invalid tile.y";

        except KeyError as e:
            error_string = 'KeyError: ' + e.args[0];
        return error_string, int(date_from), int(date_to), tiles

    elif method == 'GET_TILE_DETAIL_INFO':
        try:
            date_from = contents['date']['from']
            date_to = contents['date']['to']
            tile = contents['tile']
            
            level = -1;
            x = -1;
            y = -1;

            level = tile['level'];
            x = tile['x']
            y = tile['y']
            
            if level < 9 or level > 13:
                error_string = "Invalid tile.level";
            if x < 0:
                error_string = "Invalid tile.x";
            if y < 0:
                error_string = "Invalid tile.y";

        except KeyError as e:
            error_string = 'KeyError: ' + e.args[0];
        return error_string, int(date_from), int(date_to), tiles       

    return error_string;

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

    logging.info('Request from %s: %s', request.remote_addr, contents);

    error_string, parameters, exclusiveness, topic_count, word_count, date, include_words, exclude_words, tiles = checkInputValidation('GET_TOPICS', contents);
    if error_string != "Success":
        logging.error('ERROR_BAD_REQUEST: %s', error_string);
        return error_string, status.HTTP_400_BAD_REQUEST;

    # print request values
    logging.debug('exclusiveness: %s', exclusiveness);
    logging.debug('topic_count: %s', topic_count);
    logging.debug('word_count: %s', word_count);
    logging.debug('date: %s', date);
    for word in include_words:
        logging.debug('include words: %s', word);
    for word in exclude_words:
        logging.debug('exclude words: %s', word);
    for tile in tiles:
        logging.debug('x: %s, y: %s, level: %s', tile['x'], tile['y'], tile['level']);
    
    # run topic modeling for each tile
    topics = [];
    for tile in tiles:

        level = tile['level'];
        x = tile['x']
        y = tile['y']

        # change parameters form default set_params to json input. 
        topic = TM.get_topics(level, x, y, topic_count, word_count, include_words, exclude_words, exclusiveness, date);
        topics.append(topic);

    # verify that the calculation is correct using log.
    for topic in topics:
        logging.debug('topic: %s', topic)

    json_data = json.dumps(topics);

    return json_data;

@app.route('/GET_RELATED_DOCS/<uuid>', methods=['POST'])
def request_get_related_docs(uuid):

    contents = request.get_json(silent=True);

    logging.info('Request from %s: %s', request.remote_addr, contents);

    error_string, word, level, x, y, date = checkInputValidation('GET_RELATED_DOCS', contents);
    if error_string != "Success":
        logging.error('ERROR_BAD_REQUEST: %s', error_string);
        return error_string, status.HTTP_400_BAD_REQUEST;

    # run topic modeling for each tile
    docs = [];
    docs = TM.get_related_docs(level, x, y, word, date);

    # verify that the calculation is correct using log.
    # doc_list = docs['documents'];
    logging.debug('found %d doc(s)', len(docs));
    
    # for idx, doc in enumerate(docs):
    #     # logging.debug('[%d]created_at: %s', idx, doc['created_at']);
    #     # logging.debug('[%d]text: %s', idx, doc['text'].encode('utf-8'));
    #     #logging.debug('')
    #     logging.debug(doc)
    

    json_data = json.dumps(docs);

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


#--- add new protocol
@app.route('/GET_TILE_DETAIL_INFO/<uuid>', methods=['POST'])
def request_get_tile_detail_info(uuid):

    logging.info('Request from %s: %s', request.remote_addr, contents);

    error_string, date_from, date_to, tile = checkInputValidation('GET_TILE_DETAIL_INFO', contents);
    if error_string != "Success":
        logging.error('ERROR_BAD_REQUEST: %s', error_string);
        return error_string, status.HTTP_400_BAD_REQUEST;

    logging.debug('date_from: %d', date_from);
    logging.debug('date_to: %d', date_to);
    logging.debug('x: %s, y: %s, level: %s', tile['x'], tile['y'], tile['level']);

    output = []
    
    level = tile['level']
    x = tile['x']
    y = tile['y']

    output = TM.get_tile_detail_info(level, x, y, time_from, time_to);
    outputs.append(output)

    for output in outputs:
        logging.debug('output: %s', output)

    json_data = json.dumps(outputs);

    return json_data 

@app.route('/GET_HEATMAP/<uuid>', methods=['POST'])
def request_get_heatmap(uuid):

    contents = request.get_json(silent=True);

    logging.info('Request from %s: %s', request.remote_addr, contents);

    error_string, date_from, date_to, tiles = checkInputValidation('GET_HEATMAP', contents);
    if error_string != "Success":
        logging.error('ERROR_BAD_REQUEST: %s', error_string);
        return error_string, status.HTTP_400_BAD_REQUEST;

    logging.debug('date_from: %d', date_from);
    logging.debug('date_to: %d', date_to);
    for tile in tiles:
        logging.debug('x: %s, y: %s, level: %s', tile['x'], tile['y'], tile['level']);

    heatmap_list = []
    for tile in tiles:
        level = tile['level'];
        x = tile['x']
        y = tile['y']
        heatmaps = TM.get_heatmaps(level, x, y, date_from, date_to);
        for heatmap in heatmaps:
            heatmap_list.append(heatmap)

    for heatmap in heatmap_list:
        logging.debug('heatmap: %s', heatmap)

    json_data = json.dumps(heatmap_list);

    return json_data 

if __name__ == '__main__':

    initProject()

    DB = database_wrapper.DBWrapper()
    DB.connect("localhost", constants.DEFAULT_MONGODB_PORT)
    TM = topic_modeling_module.TopicModelingModule(DB)
    TG = tile_generator.TileGenerator(DB)

    app.run(host='0.0.0.0', port='5002')
