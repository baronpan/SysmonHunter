from elasticsearch import Elasticsearch, helpers
import pandas

from utils.log import *

class ES(object):
    def __init__(self, conf):
        self.es = Elasticsearch([conf['es_host']])
        self.winlogbeat = conf['winlogbeat_index']

    def insert_behaviors(self, _index, data):
        records = []
        for _be in data:
            _cols = _be.get_attribute_names()
            _record = _be.serialize()
            
            try:
                records.append({
                    '_index': _index + _be.getname().lower(),
                    '_type': 'behavior',
                    '_source': pandas.DataFrame([_record], columns=_cols).loc[0].to_json(default_handler=str),
                })
            except Exception as e:
                log_error('Elasticsearch insert failed. {}'.format(e))
                log_error(pandas.DataFrame([_record], columns=_cols).loc[0])
            
        helpers.bulk(self.es, records)

    def query(self, _index, doctype, qstring):
        records = []
        try:
            page = self.es.search(index=_index, doc_type=doctype, scroll='2m', size=1000, q=qstring, timeout='10m')
            sid = page['_scroll_id']
            scroll_size = page['hits']['total']
            docs = page['hits']['hits']
            records += [x['_source'] for x in docs]
            
            while scroll_size > 0:
                page = self.es.scroll(scroll_id=sid, scroll='5m')
                sid = page['_scroll_id']
                scroll_size = len(page['hits']['hits'])
                docs = page['hits']['hits']
                records += [x['_source'] for x in docs]
            return pandas.DataFrame(records)
        except Exception as e:
            log_error('Elasticsearch query failed. {}'.format(e))
            return pandas.DataFrame([])