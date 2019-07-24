
from utils.log import *

def _df_columns_statistic(data, cols):
    subdata = data.dropna(subset=cols, how='all')
    gpdata = subdata.groupby(by=cols).size().sort_values(ascending=False)
    
    # for debugging.
    #print gpdata.describe()
    
    return gpdata
    

def st_output(gpdata):
    result = []
    for _value, _count in gpdata.iteritems():
        if type(_value) is list or type(_value) is tuple:
            _value = '|'.join(_value)
            result.append([_value, _count])
        else:
            result.append([_value, _count])
    return result

def st_procchain(data):
    result = _df_columns_statistic(data, ['parent.image', 'current.image'])
    return result

def st_network(data, cols):
    result = _df_columns_statistic(data, cols)
    return result

def st_reg(data):
    result = _df_columns_statistic(data, ['reg.path'])
    return result

def st_file(data):
    result = _df_columns_statistic(data, ['file.path'])
    return result