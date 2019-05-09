import os
import json
import re
from visualizeSpecies import VisualizeSpecies
from visualizeFunction import VisualizeFunction


class VisualizeAll(VisualizeSpecies):
    """
    Sample usage:
        from visualizeAll import VisualizeAll
        VisualizeAll("/home/cheng/Projects/rll_testdir/mapping_file.txt","Group1").visualize()
    """

    def __init__(self, mapping_file, categories=False, out_dir=False, exclude_species="UNREALTAX"):
        super(VisualizeAll, self).__init__("multi_table", mapping_file,
                                           categories, out_dir=out_dir, exclude_species=exclude_species)
        self.out_dir = out_dir if out_dir else os.path.dirname(self.mapping_file) + '/'
        self._base_dir = os.path.dirname(__file__) + '/'

    def visualize(self):
        os.system("{}/piputils/write_colors_plan.py -i {} -c {} -p {}/piputils/group_color.list -o {}colors_plan.json".format(
            self.path['bayegy_home'], self.mapping_file, self.categories, self.path['bayegy_home'], self.out_dir))
        os.environ['COLORS_PLAN_PATH'] = self.out_dir + 'colors_plan.json'
        for abundance_table in [self.out_dir + 'FMAP/' + f for f in ('All.Function.abundance.KeepID.KO.txt', 'All.Function.abundance.KeepID.Module.txt', 'All.Function.abundance.KeepID.Pathway.txt', 'All.Function.abundance.KeepID.Pathway.Level1.txt', 'All.Function.abundance.KeepID.Pathway.Level2.txt')] + [self.out_dir + 'AMR' + '/All.AMR.abundance.txt']:
            VisualizeFunction(abundance_table, self.mapping_file, self.categories).visualize()
        VisualizeSpecies(self.out_dir + 'Kraken2/All.Taxa.OTU.txt', self.mapping_file,
                         self.categories, exclude_species=self.exclude_species).visualize()
        os.system("cd {}&&bash {}orgnize_dir_structure.sh {} {}".format(self.out_dir,
                                                                        self._base_dir, self.mapping_file, re.sub(',.*$', '', self.categories)))