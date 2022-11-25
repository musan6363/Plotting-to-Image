from glob import glob
import json
import ndjson
from os import path as osp

def cnt_checked(json_path):
    try:
        with open(json_path, 'r') as f:
            _ndj = ndjson.load(f)
            _tmp = json.dumps(_ndj)
            _data = json.loads(_tmp)
        return len(_data)
    except FileNotFoundError:
        return 0


ann_records = glob('./annotation-check-result/ann_records/*.json')
cnt_ann = {}

for ann_record in ann_records:
    _tmp = osp.splitext(osp.basename(ann_record))[0].split('_')
    _dataset = _tmp[0]
    _version = _tmp[1]
    with open(ann_record, 'r') as f:
        _data = json.load(f)
    cnt_ann[_dataset+'/'+_version] = {}
    cnt_ann[_dataset+'/'+_version]['annotated'] = len(_data)

for target in cnt_ann.keys():
    _path_not_use = 'annotation-check-result/output/'+target+'/checked_ann_not_use.json'
    _path_re_do = 'annotation-check-result/output/'+target+'/checked_ann_re_do.json'

    cnt_ann[target]['not-use'] = cnt_checked(_path_not_use)
    cnt_ann[target]['re-do'] = cnt_checked(_path_re_do)
    cnt_ann[target]['valid'] = cnt_ann[target]['annotated'] - cnt_ann[target]['not-use'] - cnt_ann[target]['re-do']

for dst in cnt_ann.items():
    print(dst)