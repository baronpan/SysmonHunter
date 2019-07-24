from neo4j.v1 import GraphDatabase
from core.behavior import *
from core.entity import *

class Neo4jGraph(object):
    def __init__(self, conf):
        self.db = GraphDatabase.driver(conf['neo4j_host'], auth=(conf['neo4j_user'], conf['neo4j_pwd']))

    def update_behaviors(self, data):
        for _behav in data:
            with self.db.session() as session:
                tx = session.begin_transaction()
                if isinstance(_behav, ProcessBehavior):
                    self.update_procchain(tx, _behav)
                elif isinstance(_behav, RegistryBehavior):
                    self.update_reg(tx, _behav)
                elif isinstance(_behav, FileBehavior):
                    self.update_file(tx, _behav)
                elif isinstance(_behav, NetworkBehavior):
                    self.update_network(tx, _behav)
                tx.commit()

    def __update_records(self, tx, src_nd, dst_nd, rel, ts):
        src_name = src_nd[1].strip().replace('\\', '\\\\').replace('\'', '\\\'')
        dst_name = dst_nd[1].strip().replace('\\', '\\\\').replace('\'', '\\\'')
        if src_name == '' or dst_name == '':
            return
            
        src_props = ', '.join(["src.{} = '{}'".format(k,v) for k,v in src_nd[2].iteritems()])
        if src_props != '':
            src_props = ', ' + src_props
        dst_props = ', '.join(["dst.{} = '{}'".format(k,v) for k,v in dst_nd[2].iteritems()])
        if dst_props != '':
            dst_props = ', ' + dst_props
        _sql = "MERGE (src:{0} {{ name: '{1}' }}) \
                ON CREATE SET src.first_seen = '{2}' {3} \
                ON MATCH SET src.last_seen = '{2}' {3} \
                RETURN src".format(src_nd[0], src_name, ts, src_props)
        tx.run(_sql)

        _sql = "MERGE (dst:{0} {{ name: '{1}' }}) \
                ON CREATE SET dst.first_seen = '{2}' {3} \
                ON MATCH SET dst.last_seen = '{2}' {3} \
                RETURN dst".format(dst_nd[0], dst_name, ts, dst_props)
        tx.run(_sql)

        _sql = "MATCH (src:{} {{ name: '{}' }}), (dst:{} {{ name: '{}' }}) \
                MERGE (src)-[r:{}]->(dst) \
                RETURN src, r, dst".format(src_nd[0], src_name,
                dst_nd[0], dst_name, rel)
        tx.run(_sql)

    def __update_process(self, tx, proc, _mid, _timestamp, _behav):
        img_path = proc['image']
        self.__update_records(tx, 
            ['path', img_path, {}],
            ['epuuid', _mid, {}],
            'related', _timestamp)
        self.__update_records(tx, 
            _behav,
            ['path', img_path, {}],
            'use', _timestamp)

    def __update_file(self, tx, _file, _mid, _timestamp, _behav):
        filepath = _file['path']
        filehash = _file['hash']
        self.__update_records(tx, 
            ['path', filepath, {}],
            ['epuuid', _mid, {}],
            'related', _timestamp)
        self.__update_records(tx, 
            ['hash', filehash, {}],
            ['epuuid', _mid, {}],
            'related', _timestamp)
        self.__update_records(tx, 
            _behav,
            ['path', filepath, {}],
            'use', _timestamp)
        self.__update_records(tx, 
            _behav,
            ['hash', filehash, {}],
            'use', _timestamp)

    def __update_network(self, tx, network, _mid, _timestamp, _behav):
        domain = network['rhost']
        ip = network['rip']

        self.__update_records(tx, 
            ['domain', domain, {}],
            ['epuuid', _mid, {}],
            'related', _timestamp)
        self.__update_records(tx, 
            ['ip', ip, {}],
            ['epuuid', _mid, {}],
            'related', _timestamp)
        self.__update_records(tx, 
            _behav,
            ['domain', domain, {}],
            'use', _timestamp)
        self.__update_records(tx, 
            _behav,
            ['ip', ip, {}],
            'use', _timestamp)
        self.__update_records(tx, 
            ['ip', ip, {}],
            ['domain', domain, {}],
            'bind', _timestamp)

    def __update_reg(self, tx, reg, _mid, _timestamp, _behav):
        reg_value = '{}({})'.format(reg['path'], reg['key'])
        self.__update_records(tx, 
            ['reg', reg_value, {}],
            ['epuuid', _mid, {}],
            'related', _timestamp)
        self.__update_records(tx, 
            _behav,
            ['reg', reg_value, {}],
            'use', _timestamp)

    def update_procchain(self, tx, behav):
        _timestamp = behav.date
        _relation = behav.relation
        _mid = behav.endpoint['uuid']
        behav_node = ['processbehav', behav.get_value(), {'attckids': behav.attck_ids}]

        self.__update_records(tx, 
            behav_node,
            ['epuuid', _mid, {}],
            'impact', _timestamp)
        self.__update_process(tx, behav.parent, _mid, _timestamp, behav_node)
        self.__update_process(tx, behav.current, _mid, _timestamp, behav_node)
        self.__update_file(tx, behav.file, _mid, _timestamp, behav_node)

    def update_reg(self, tx, behav):
        _timestamp = behav.date
        _relation = behav.relation
        _mid = behav.endpoint['uuid']
        behav_node = ['regbehav', behav.get_value(), {'attckids': behav.attck_ids}]

        self.__update_records(tx, 
            behav_node,
            ['epuuid', _mid, {}],
            'impact', _timestamp)
        self.__update_process(tx, behav.process, _mid, _timestamp, behav_node)
        self.__update_file(tx, behav.file, _mid, _timestamp, behav_node)
        self.__update_reg(tx, behav.reg, _mid, _timestamp, behav_node)


    def update_file(self, tx, behav):
        _timestamp = behav.date
        _relation = behav.relation
        _mid = behav.endpoint['uuid']
        behav_node = ['filebehav', behav.get_value(), {'attckids': behav.attck_ids}]

        self.__update_records(tx, 
            behav_node,
            ['epuuid', _mid, {}],
            'impact', _timestamp)
        self.__update_process(tx, behav.process, _mid, _timestamp, behav_node)
        self.__update_file(tx, behav.file, _mid, _timestamp, behav_node)

    def update_network(self, tx, behav):
        _timestamp = behav.date
        _relation = behav.relation
        _mid = behav.endpoint['uuid']
        behav_node = ['netbehav', behav.get_value(), {'attckids': behav.attck_ids}]

        self.__update_records(tx, 
            behav_node,
            ['epuuid', _mid, {}],
            'impact', _timestamp)
        self.__update_process(tx, behav.process, _mid, _timestamp, behav_node)
        self.__update_network(tx, behav.network, _mid, _timestamp, behav_node)
        self.__update_file(tx, behav.file, _mid, _timestamp, behav_node)

    def query_node_degree(self, ntype):
        with self.db.session() as session:
            _sql = "MATCH (a:{}) RETURN a.name, size((a)-->()) as out, size((a)<--()) as in".format(ntype)
            tx = session.begin_transaction()
            result = tx.run(_sql).values()
            tx.commit()
            return result

    def delete_node(self, ntype, nvalue):
        with self.db.session() as session:
            _sql = "MATCH (n:{} {{name: '{}'}})-[r]-() DELETE n,r".format(ntype, nvalue)
            tx = session.begin_transaction()
            tx.run(_sql)
            tx.commit()

    # For example [[('src id', 'src type', 'src value'), 'relation type', ('dst id', 'dst type', 'dst value')]]
    def query_node_relations(self, nvalue):
        nvalue = nvalue.replace('\\', '\\\\\\\\')
        with self.db.session() as session:
            _sql = "MATCH (src)-[r]-(dst) WHERE src.name =~ '.*{}.*' RETURN src, type(r), dst".format(nvalue)
            tx = session.begin_transaction()
            data = tx.run(_sql).values()
            result = []

            for en in data:
                result.append([
                    (en[0].id, list(en[0].labels)[0], en[0]['name']),
                    en[1],
                    (en[2].id, list(en[2].labels)[0], en[2]['name']),
                ])

            tx.commit()
            return result

NODE_TYPES = [
    'processbehav',
    'regbehav',
    'filebehav',
    'netbehav',
    'epuuid',
    'ip',
    'domain',
    'hash',
    'path',
    'reg',
]