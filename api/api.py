# api/api.py
 
#################
#### imports ####
#################
 
from app import app
from flask import render_template, Blueprint, request, jsonify
from logger import logger
from blackfynn import Blackfynn
from config import Config
from flask_marshmallow import Marshmallow
from neo4j import GraphDatabase, basic_auth
import json
import urllib
import requests
# from .simcore import init_sim_db

################
#### config ####
################
 
api_blueprint = Blueprint('api', __name__, template_folder='templates', url_prefix='/api')

bf = None
gp = None
ma = Marshmallow(app)

@app.before_first_request
def connect_to_blackfynn():
    global bf

    bf = Blackfynn(
       api_token=Config.BLACKFYNN_API_TOKEN,
       api_secret=Config.BLACKFYNN_API_SECRET,
       env_override=False,
       host=Config.BLACKFYNN_API_HOST,
       concepts_api_host=Config.BLACKFYNN_CONCEPTS_API_HOST
    )

@app.before_first_request
def connect_to_graphenedb():
    global gp
    # graphenedb_url = Config.GRAPHENEDB_BOLT_URL
    # graphenedb_user = Config.GRAPHENEDB_BOLT_USER
    # graphenedb_pass = Config.GRAPHENEDB_BOLT_PASSWORD
    # gp = GraphDatabase.driver(graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))

    # init_sim_db(gp)

#########################
#### GRAPHDB  routes ####
#########################

# API Endpoint which returns all the names of the properties that are available
# in the database.
@api_blueprint.route('/db/graph/properties')
def graph_props():
    cmd = 'MATCH (n:GraphModel)-[*1]-(m:GraphModelProp) RETURN n.name, m.name, m.type'
    with gp.session() as session:
        result = session.run(cmd)
        items = []
        for record in result:
            items.append({'model': record['n.name'], 'prop': record['m.name'], 'type': record['m.type']})

    return json.dumps(items)

# API endpoint to query the graph and return a filtered set of records for a particular model
@api_blueprint.route('/db/model/<model>')
def model(model):
    
    # Get Request parameters and stage Cypher cmd
    args = request.args

    # Get arguments for pagination
    offset = args.get('offset')
    limit = args.get('limit')

    # Get arguments for ordering of results
    order_by = args.get('orderby')
    descending = args.get('desc')

    # Get argument specifying how many hops the search should limit to
    hops = args.get('hops')

    # Get arguments that describer the filter settings
    filters = args.get('filters')

    # Get argument that optionally restricts the returned properties for a query.
    responseProps = args.get('responseProps')

    # Parse arguments
    filters = json.loads(urllib.unquote(filters)) if filters !=None else None
    responseProps = json.loads(urllib.unquote(responseProps)) if responseProps != None else None
    offset = offset if offset != None else 0
    limit = limit if limit != None else 100
    hops = hops if hops != None else 1
    descending = 'DESC' if descending == 'descending' else ''
    doReturnObjects = True

    response_str = ''
    if responseProps !=None:
        doReturnObjects = False
        for item in responseProps:
            response_str += 'n.{},'.format(item)
        
        response_str = response_str[:-1]
    else:
        response_str = 'n'

    if filters:
        cmd = ''
        # # Add MATCH statements 
        for idx, f in enumerate(filters):
            propComponents = f['m'].split(':')
            propModel = propComponents[0]
            propProperty = propComponents[1]

            if model != propModel:
                # Start MATCH query where filter-model does not equal output model
                cmd += 'MATCH '

                # Get path between source and target model
                path_cmd = 'MATCH (n:GraphModel {{name: "{}"}}), (m:GraphModel {{name: "{}"}}), p = shortestPath( (n)-[*]-(m)) return p'.format(model, propModel)
                cur_path = {}
                with gp.session() as session:
                    result = session.run(path_cmd)    
                    for record in result:
                        cur_path = record['p'].nodes
                
                # Parse resulting path into CYPHER query
                for idx2, item in enumerate(cur_path):
                    if idx2 == 0:
                        cmd += '(n:{}) '.format(item['name'])
                    elif idx2 < (len(cur_path) - 1):
                        cmd += '-- (:{}) '.format(item['name'])
                    else:
                        cmd += '-- (m{}:{}) '.format(idx, item['name'])                    

            elif idx == 0:
                # Start MATCH query where filter-model equals output model (no hops).
                cmd += 'MATCH (n:{}) '.format(model)

        # Add WHERE statements
        for idx, f in enumerate(filters):
            if idx > 0:
                cmd += 'AND '
            else :
                cmd += 'WHERE '

            valueStr = f['v']
            # print(f['o'])
            if f['o'] in ['STARTS WITH', 'ENDS WITH', 'CONTAINS']:
                print(f['o'])
                valueStr = "'{}'".format(f['v'])
            elif f['o'] == 'IS':
                f['o'] = '='
                valueStr = "'{}'".format(f['v'])

            # print('filter: {} + {} + {}'.format(f['m'],f['o'],valueStr))

            propComponents = f['m'].split(':')
            propModel = propComponents[0]
            propProperty = propComponents[1]
            if model == propModel:
                cmd += 'n.{} {} {} '.format(propProperty, f['o'], valueStr)
            else:
                cmd += 'm{}.{} {} {} '.format(idx, propProperty, f['o'], valueStr)

        # Add RETURN
        cmd += 'RETURN distinct {}'.format(response_str)

        # Set Order Info
        if order_by:
            cmd += ' ORDER BY n.{} {}'.format(order_by, descending)

        # Set Pagination Info
        cmd += ' SKIP {} LIMIT {}'.format( offset, limit)

    else:
        if order_by:
            cmd = 'MATCH (n:{}) RETURN n ORDER BY n.{} {} SKIP {} LIMIT {}'.format(model, order_by, descending, offset, limit)
        else:
            cmd = 'MATCH (n:{}) RETURN n SKIP {} LIMIT {}'.format(model, offset, limit)
        
    # print('requesting: {}'.format(cmd))    
    resp = []
    with gp.session() as session:
        result = session.run(cmd)    
        if doReturnObjects:
            # Return records
            for record in result:
                keys = record['n'].keys()
                item = {}
                for key in keys:
                    item[key] = record['n'][key]

                resp.append(item)       
        else:       
            # Return list of propValues
            resp = {}
            for record in result:
                keys = record.keys()
                for key in keys:
                    if key not in resp:
                        resp[key] = list()

                    resp[key].append(record[key])

    return json.dumps(resp)

@api_blueprint.route('/db/model/<model>/props')
def getLabelProps(model):
    cmd = 'MATCH (a:{}) UNWIND keys(a) AS key RETURN collect(distinct key)'.format(model)

    # cmd = 'MATCH (n:{}) RETURN n LIMIT 1'.format(model)
    # print(cmd)

    resp = []
    with gp.session() as session:
        result = session.run(cmd) 
        # print(result)
        for k in result:
            col = k['collect(distinct key)']
            for item in col:
                resp.append(item)

    return json.dumps(resp)

@api_blueprint.route('/db/labels')
def getLabel():
    cmd = 'MATCH (n:Node) RETURN DISTINCT LABELS(n)'
    resp = list()
    with gp.session() as session:
        result = session.run(cmd)  
        for record in result:
            resp.append(record['LABELS(n)'][1])
    
    return json.dumps(resp)

# API Endpoint which returns the range of the values for a particular property if the 
# property is a numeric.
@api_blueprint.route('/db/graph/<model>/<prop>/range')
def getNumericPropRange(model, prop):
    cmd = 'MATCH (n:{}) RETURN max(n.{}) as max, min(n.{}) as min'.format(model,prop,prop)
    resp = {}
    with gp.session() as session:
        result = session.run(cmd)
        for k in result:
            resp['min'] = k['min']
            resp['max'] = k['max']
    
    return json.dumps(resp)


# API Endpoint to return neighbouring models at n hops away from active model
# This endpoint leverages the fact that we store the graph topology in the 
# Graph database using the 'GraphModel' labels.
@api_blueprint.route('/db/graph/model/<model>/hops/<hops>')
def getNeighborModels(model, hops):

    cmd = 'MATCH (n:GraphModel) -[*0..{}]- (m:GraphModel {{name:"{}"}}) RETURN DISTINCT n.name'.format(hops, model)
    resp = list()
    with gp.session() as session:
        result = session.run(cmd)         
        for k in result:
            resp.append(k['n.name'])

    return json.dumps(resp)

#########################
#### DAT-CORE routes ####
#########################

# Returns a list of public datasets from 
@api_blueprint.route('/datasets')
def discover():
    resp = bf._api._get('/consortiums/1/datasets')
    return json.dumps(resp)

#########################
#### MAP-CORE routes ####
#########################


#########################
#### SIM-CORE routes ####
#########################

import logging

@api_blueprint.route('/sim/dataset')
def datasets():
    if request.method == 'GET':
        query = request.args.get('query')
        req = requests.get('{}/search/datasets?query={}'.format(Config.DISCOVER_API_HOST, query))
        json = req.json()
        # Filter only datasets with tag 'simcore'
        json['datasets'] = filter(lambda dataset: ('simcore' in dataset.get('tags', [])), json.get('datasets', []))
        return jsonify(json)

@api_blueprint.route('/sim/dataset/<id>')
def dataset(id):
    if request.method == 'GET':
        req = requests.get('{}/datasets/{}'.format(Config.DISCOVER_API_HOST, id))
        json = req.json()
        inject_markdown(json)
        inject_template_data(json)
        return jsonify(json)

def inject_markdown(resp):
    if 'readme' in resp:
        mark_req = requests.get(resp.get('readme'))
        resp['markdown'] = mark_req.text

def inject_template_data(resp):
    import boto3
    from botocore.exceptions import ClientError
    import json

    id = resp.get('id')
    version = resp.get('version')
    if (id is None or version is None):
        return

    try:
        s3_client = boto3.Session().client('s3', region_name='us-east-1')
        response = s3_client.get_object(Bucket='blackfynn-discover-use1',
                                        Key='{}/{}/packages/template.json'.format(id, version),
                                        RequestPayer='requester')
    except ClientError as e:
        logging.error(e)
        return

    template = response['Body'].read()

    try:
        template_json = json.loads(template)
    except ValueError as e:
        logging.error(e)
        return

    resp['study'] = {'uuid': template_json.get('uuid'),
                     'name': template_json.get('name'),
                     'description': template_json.get('description')}
