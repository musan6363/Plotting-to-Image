import json
import ndjson
import os
import shutil

class MakeReannotateList:
    def __init__(self, dataset, version) -> None:
        self.dataset_name = dataset
        self.dataset_version = version

        self.ori_annotated_dir = 'ann/'+self.dataset_name+'/'+self.dataset_version+'/json'
        self.checked_json = 'output/'+self.dataset_name+'/'+self.dataset_version+'/checked_ann_re_do.json'

        self.save_path = 'reannotate/'+self.dataset_name+'/'+self.dataset_version
        os.makedirs(self.save_path+'/img', exist_ok=True)
        self.reaanotate_json = self.save_path+'/reannotate.json'
        self.recheck_json = 'output/'+self.dataset_name+'/'+self.dataset_version+'/recheck.json'

    def read_ndjson(self, file_path):
        with open(file_path, 'r') as f:
            _ndj = ndjson.load(f)
            _tmp = json.dumps(_ndj)
            _data = json.loads(_tmp)
        return _data

    def compare_annotate_result(self, img_name, ped_token, copied_look):
        _ori_ann_path = self.ori_annotated_dir + '/' + img_name + '.json'
        _ori_ann_records = self.read_ndjson(_ori_ann_path)
        for record in _ori_ann_records:
            if record['token'] == ped_token:
                break
        if record['look'] == copied_look:
            return record
        else:
            raise ValueError("jsonファイルのコピーに失敗しています", img_name, ped_token)

    def make_list(self):
        self.reannotate_list = []
        self.recheck_dict = {}
        for d in self.reannotate_target:
            for token, record in d.items():
                _img_name = record['img_name']
                _ped_token = record['ped_token']
                _look = record['look']
                _ori_ann_record = self.compare_annotate_result(_img_name, _ped_token, _look)
                self.reannotate_list.append({
                    'img_token' : _img_name,
                    'ped_token' : _ped_token,
                    'bbox' : _ori_ann_record['bbox'],
                    'look' : _look,
                    'eyecontact' : _ori_ann_record['eyecontact'],
                    'difficult' : _ori_ann_record['difficult'],
                    'memo' : record['memo']
                })
                _recheck_dst = {}
                _recheck_dst[token] = record.copy()
                _ = _recheck_dst[token].pop('memo')
                self.recheck_dict.update(_recheck_dst)
                self.copy_img(_img_name, _ped_token)

    def copy_img(self, img_token, ped_token):
        shutil.copy2('output/'+self.dataset_name+'/'+self.dataset_version+'/img/'+ped_token+'@'+img_token+'.png', self.save_path+'/img/')

    def export(self):
        with open(self.reaanotate_json, 'w', encoding='utf-8') as f:
            json.dump(self.reannotate_list, f, indent=2, ensure_ascii=False)
        with open(self.recheck_json, 'w', encoding='utf-8') as f:
            json.dump(self.recheck_dict, f, indent=2, ensure_ascii=False)

    def main(self):
        self.reannotate_target = self.read_ndjson(self.checked_json)
        self.make_list()
        self.export()
        print(self.reannotate_list, end='\n\n')
        print(self.recheck_dict)


if __name__ == "__main__":
    mrl = MakeReannotateList('nuimages_ped', 'v1.0-train')
    mrl.main()