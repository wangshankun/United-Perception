import os
import io
import torch
import json
import time

from collections import defaultdict

from pycocotools.coco import COCO


class PetrelOpen(object):
    def __init__(self, filename, **kwargs):
        self.handle = PetrelHelper._petrel_helper.load_data(filename, **kwargs)

    def __enter__(self):
        return self.handle

    def __exit__(self, exc_type, exc_value, exc_trackback):
        del self.handle


class PetrelHelper(object):

    _petrel_helper = None
    open = PetrelOpen

    def __init__(self, conf_path='~/petreloss.conf'):
        self.conf_path = conf_path

        self._inited = False

        self._init_petrel()

        PetrelHelper._petrel_helper = self

    def _init_petrel(self):
        try:
            from petrel_client.client import Client
            self.client = Client(self.conf_path)

            self._inited = True
        except Exception as e:
            print(e)
            print('init petrel failed')

    def check_init(self):
        if not self._inited:
            raise Exception('petrel oss not inited')

    def _iter_cpeh_lines(self, path):
        response = self.client.get(path, enable_stream=True, no_cache=True)

        for line in response.iter_lines():
            cur_line = line.decode('utf-8')
            yield cur_line

    def load_data(self, path, ceph_read=True, fs_read=False):
        if 's3://' not in path:
            if not fs_read:
                return open(path)
            else:
                return open(path).read()
        else:
            self.check_init()

            if ceph_read:
                return self._iter_cpeh_lines(path)
            else:
                return self.client.get(path)

    @staticmethod
    def load_json(path):
        if 's3://' not in path:
            js = json.load(open(path, 'r'))
        else:
            js = json.loads(PetrelHelper._petrel_helper.load_data(path, ceph_read=False))
        return js

    def load_pretrain(self, path, map_location=None):
        if 's3://' not in path:
            assert os.path.exists(path), f'No such file: {path}'
            return torch.load(path, map_location=map_location)
        else:
            self.check_init()

            file_bytes = self.client.get(path)
            buffer = io.BytesIO(file_bytes)
            res = torch.load(buffer, map_location=map_location)
            return res

    @staticmethod
    def load(path, **kwargs):
        return PetrelHelper._petrel_helper.load_pretrain(path, **kwargs)


__petrel_helper = PetrelHelper()


class PetrelCOCO(COCO):
    def __init__(self, annotation_file=None):
        """
        Constructor of Microsoft COCO helper class for reading and visualizing annotations.
        :param annotation_file (str): location of annotation file
        :param image_folder (str): location to the folder that hosts images.
        :return:
        """
        # load dataset
        self.dataset, self.anns, self.cats, self.imgs = dict(), dict(), dict(), dict()
        self.imgToAnns, self.catToImgs = defaultdict(list), defaultdict(list)
        if annotation_file is not None:
            print('loading annotations into memory...')
            tic = time.time()
            dataset = PetrelHelper.load_json(annotation_file)
            assert type(dataset) == dict, 'annotation file format {} not supported'.format(type(dataset))
            print('Done (t={:0.2f}s)'.format(time.time() - tic))
            self.dataset = dataset
            self.createIndex()