# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template, request, Response
from flask import jsonify
import json

from utils.log import *
from utils.common import *
from db.es import ES
from db.graph import Neo4jGraph
from web.middleware import *
from core import attck
from db import esapi
import analyst.statistic as ast

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

@app.route('/', methods=['GET'])
def main_handler():
    return render_template('/index.html')

@app.route('/event/raw', methods=['GET'])
def event_raw_handler():
    return render_template('event_raw.html')

@app.route('/ajax/event/raw', methods=['POST'])
def ajax_event_raw():
    daterange = request.form['daterange']
    behavtype = request.form['behav']
    
    result = get_event('raw', behavtype, daterange, esapi.esapi_behavior_by_range)    
    return jsonify({'data': result})


@app.route('/event/abnormal', methods=['GET'])
def event_abnormal_handler():
    return render_template('event_abnormal.html')

@app.route('/ajax/event/abnormal', methods=['POST'])
def ajax_event_abnormal():
    daterange = request.form['daterange']
    behavtype = request.form['behav']
    
    result = get_event('abnormal', behavtype, daterange, esapi.esapi_behavior_by_range)    
    return jsonify({'data': result})

@app.route('/graphic/search', methods=['GET'])
def graphic_search_handler():
    return render_template('/graphic_search.html')

@app.route('/graphic/manage', methods=['GET'])
def graphic_manage_handler():
    return render_template('/graphic_manage.html')

@app.route('/ajax/graphic/degree', methods=['POST'])
def node_degree():
    nodetype = request.form['nodetype']
    data = server.GRAGHDB_INSTANCE.query_node_degree(nodetype)
    result = []
    for en in data:
        result.append({
            'name': en[0],
            'out': en[1],
            'in': en[2],
        })
    return jsonify({'data': result})

@app.route('/ajax/graphic/delete', methods=['POST'])
def node_delete():
    nodetype = request.form['nodetype']
    nodevalues = request.form['nodevalues']
    for nd in json.loads(nodevalues):
        server.GRAGHDB_INSTANCE.delete_node(nodetype, nd)
    return jsonify(success=True)

@app.route('/ajax/graphic/query', methods=['POST'])
def node_query():
    inputvalues = request.form['inputarea']

    nodes = {}
    edges = []
    rels = []
    for en in inputvalues.split('\n'):
        rels.extend(server.GRAGHDB_INSTANCE.query_node_relations(en.strip()))

    group_id = {
        'processbehav': 1,
        'regbehav': 2,
        'filebehav': 3,
        'netbehav': 4,
        'epuuid': 5,
        'ip': 6,
        'domain': 7,
        'hash': 8,
        'path': 9,
        'reg': 10,
    }

    for rel in rels:
        nodes[rel[0][0]] = {
            'id': rel[0][0],
            'label': 'eid:' + rel[0][2] if group_id[rel[0][1]] == 5 else rel[0][2],
            'group': group_id[rel[0][1]],
        }
        nodes[rel[2][0]] = {
            'id': rel[2][0],
            'label': 'eid:' + rel[2][2] if group_id[rel[2][1]] == 5 else rel[2][2],
            'group': group_id[rel[2][1]],
        }
        edges.append({
            'from': rel[0][0],
            'to': rel[2][0],
        })

    return jsonify({'nodes': nodes.values(), 'edges': edges})

@app.route('/statistic/behavior/process', methods=['GET'])
def st_process_handler():
    return render_template('st_process.html')

@app.route('/ajax/statistic/behavior/process/list', methods=['POST'])
def st_procchain():
    daterange = request.form['daterange']
    
    st_data = get_statistic_data('abnormal', 'ProcessBehavior', daterange, ast.st_procchain)
    result = []
    for en in st_data:
        result.append({
            'parentimage': en[0].split('|')[0],
            'currentimage': en[0].split('|')[1],
            'count': en[1]
        })
    return jsonify({'data': result})

@app.route('/ajax/statistic/behavior/process/detail', methods=['POST'])
def detail_procchain():
    parent_value = request.form['parentcond'].replace('\\', '\\\\')
    current_value = request.form['currentcond'].replace('\\', '\\\\')
    daterange = request.form['daterange']
    conds = {
        'parent.image': parent_value,
        'current.image': current_value,
    }
    result = get_st_details_data('abnormal', 'ProcessBehavior', daterange, conds)
    return jsonify({'data': result})

@app.route('/statistic/behavior/network', methods=['GET'])
def st_network_handler():
    return render_template('st_network.html')

@app.route('/ajax/statistic/behavior/network/list', methods=['POST'])
def st_network():
    net_value = request.form['netcond']
    daterange = request.form['daterange']
    
    st_data = get_statistic_data('abnormal', 'NetworkBehavior', daterange, ast.st_network, cols=['network.' + net_value])
    result = []
    for en in st_data:
        result.append({
            'netinfo': en[0],
            'count': en[1]
        })
    return jsonify({'data': result})

@app.route('/ajax/statistic/behavior/network/detail', methods=['POST'])
def detail_network():
    net_col = request.form['netcond']
    daterange = request.form['daterange']
    net_value = request.form['netvalue']
    conds = {
        'network.' + net_col: net_value.replace('\\', '\\\\'),
    }
    result = get_st_details_data('abnormal', 'NetworkBehavior', daterange, conds)
    return jsonify({'data': result})

@app.route('/statistic/behavior/file', methods=['GET'])
def st_file_handler():
    return render_template('st_file.html')

@app.route('/ajax/statistic/behavior/file/list', methods=['POST'])
def st_file():
    daterange = request.form['daterange']
    
    st_data = get_statistic_data('abnormal', 'FileBehavior', daterange, ast.st_file)
    result = []
    for en in st_data:
        result.append({
            'filepath': en[0],
            'count': en[1]
        })
    return jsonify({'data': result})

@app.route('/ajax/statistic/behavior/file/detail', methods=['POST'])
def detail_file():
    file_cond = request.form['filecond']
    daterange = request.form['daterange']
    conds = {
        'file.path': file_cond.replace('\\', '\\\\'),
    }
    result = get_st_details_data('abnormal', 'FileBehavior', daterange, conds)
    return jsonify({'data': result})

@app.route('/statistic/behavior/registry', methods=['GET'])
def st_reg_handler():
    return render_template('st_reg.html')

@app.route('/ajax/statistic/behavior/registry/list', methods=['POST'])
def st_registry():
    daterange = request.form['daterange']
    
    st_data = get_statistic_data('abnormal', 'RegistryBehavior', daterange, ast.st_reg)
    result = []
    for en in st_data:
        result.append({
            'regpath': en[0],
            'count': en[1]
        })
    return jsonify({'data': result})

@app.route('/ajax/statistic/behavior/registry/detail', methods=['POST'])
def detail_registry():
    reg_cond = request.form['regcond']
    daterange = request.form['daterange']
    conds = {
        'reg.path': reg_cond.replace('\\', '\\\\'),
    }
    result = get_st_details_data('abnormal', 'RegistryBehavior', daterange, conds)
    return jsonify({'data': result})

@app.route('/endpoint', methods=['GET'])
def endpoint_handler():
    return render_template('endpoint.html')

@app.route('/ajax/endpoint/abnormal', methods=['POST'])
def ajax_endpoint_abnormal():
    daterange = request.form['daterange']
    behavtype = request.form['behav']
    endpoint = request.form['epid']
    
    result = get_event('abnormal', behavtype, daterange, esapi.esapi_epid_behavior_by_range, epid=endpoint)    
    return jsonify({'data': result})

ES_INSTANCE = None
GRAGHDB_INSTANCE = None
ATTCK_TECHS = None 

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', help='conf file')

    args = parser.parse_args()
    if not args.c:
        parser.print_usage()
        sys.exit()

    conf = parse_conf(args.c)

    server.ES_INSTANCE = ES(conf)
    server.GRAGHDB_INSTANCE = Neo4jGraph(conf)
    server.ATTCK_TECHS = attck.load_attcks(conf['attck_yaml'])
    app.run()