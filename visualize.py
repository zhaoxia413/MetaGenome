import os
import re
import json
from abc import ABCMeta, abstractmethod


class Visualize(metaclass=ABCMeta):
    """docstring for Visualize"""

    def __init__(self, abundance_table, mapping_file=False, categories=False, prefix=False, out_dir=False):
        out_dir = out_dir if out_dir else os.path.dirname(abundance_table)
        self.out_dir = os.path.abspath(out_dir) + '/'
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self._base_dir = os.path.dirname(__file__) + '/'
        with open(self._base_dir + "pipconfig/path.conf") as f:
            self.path = json.load(f)
        self.abundance_table = os.path.abspath(abundance_table)
        self.mapping_file = os.path.abspath(mapping_file) if mapping_file else ''
        self.categories = categories if categories else ""
        p_prefix = re.sub('\.[^\.]*$', '', os.path.basename(self.abundance_table))
        p_prefix = re.sub('^.*abundance\.KeepID\.', '', p_prefix)
        p_prefix = p_prefix.replace('All.', '').replace('.abundance', '')
        self.prefix = prefix if prefix else p_prefix + '_'
        # self.running_bash = self.out_dir + 'visualize_function.sh'

    @abstractmethod
    def __visualize_with_group__():
        pass

    @abstractmethod
    def __visualize_without_group__():
        pass

    def visualize(self, exclude='all'):
        if self.categories and self.mapping_file:
            print("Visualize using group info...")
            self.__visualize_with_group__(exclude)
        else:
            print("No group info detected, visualize without group info")
            self.__visualize_without_group__()
