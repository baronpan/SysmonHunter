# -*- coding: utf-8 -*-
import os

def recurse_dir(rootdir):
    for ens in os.listdir(rootdir):
        path = os.path.join(rootdir, ens)
        if os.path.isdir(path):
            for p in recurse_dir(path):
                yield p
        else:
            yield path

def parse_conf(conf_file):
    with open(conf_file, 'r') as f:
        configs = f.readlines()
        dict_conf = {c.split('=')[0].strip(): c.split('=')[1].strip() for c in configs }
        return dict_conf