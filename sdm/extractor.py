"""
Extractor for gridded data

y.wang@bom.gov.au
"""

from .cod import CoD
from .mask import MaskReader
from .gridded import AwapDailyDataReader, Data2D


class GriddedExtractor(object):

    def __init__(self, cod_base_dir=None, mask_base_dir=None, gridded_base_dir=None):
        self.cod_manager = CoD(base_dir=cod_base_dir)
        self.mask_reader = MaskReader(base_dir=mask_base_dir)
        self.awap_reader = AwapDailyDataReader(base_dir=gridded_base_dir)

    def extract(self, main_parameters, region=None, cube=True):
        cod_dates = self.cod_manager.read(main_parameters)
        mask = self.mask_reader.read(region or main_parameters.region_type)
        data2d = Data2D(self.awap_reader.read(main_parameters.predictand, cod_dates['adates'], mask),
                        cod_dates['rdates'],
                        mask.gpnames)

        if cube:
            return data2d.to_3d(mask.crop())
        else:
            return data2d
