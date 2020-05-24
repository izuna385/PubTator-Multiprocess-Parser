import argparse
import sys, json
from distutils.util import strtobool

class Config:
    def __init__(self):
        parser = argparse.ArgumentParser(description='PubTatorParser')
        parser.add_argument('-pickled_doc_dir', action="store", default='./pickled_doc_dir/', type=str)
        parser.add_argument('-spacy_model', action="store", default='en_core_sci_sm', type=str)
        parser.add_argument('-datadir', action="store", default='./dataset/', type=str)
        self.opts = parser.parse_args(sys.argv[1:])
        print('\n===PARAMETERS===')
        for arg in vars(self.opts):
            print(arg, getattr(self.opts, arg))
        print('===PARAMETERS END===\n')

    def get_params(self):
        return self.opts
