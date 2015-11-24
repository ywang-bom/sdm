"""
Helper program that manages CoD files

y.wang@bom.gov.au
"""
import os
from datetime import datetime

import numpy as np

from .parameters import MainParameters


class CoD(object):
    def __init__(self, base_dir=None, verbose=False):
        self.base_dir = base_dir or os.getcwd()
        self.verbose = verbose

    @staticmethod
    def calc_dates(cod_dates):
        """
        Calculate the date components, e.g. yyyy, mm, dd for the given CoD Dates list
        """
        yyyymms = cod_dates / 100 + 190000
        yyyys = yyyymms / 100
        mmdds = cod_dates % 10000
        mms = mmdds / 100
        dds = mmdds % 100

        return {
            'yyyy': yyyys,
            'mm': mms,
            'dd': dds,
            'mmdd': mmdds,
            'yyyymm': yyyymms,
        }

    @staticmethod
    def format_dates(cod_dates, format_str='%Y-%m-%d'):
        """
        Format the given CoD dates using the given format string.
        :param cod_dates:
        :type cod_dates: int
        :param format_str:
        :type format_str: str
        :return:
        :rtype:
        """
        dates = [datetime.strptime(str(d), '%Y%m%d').date().strftime(format_str)
                 for d in cod_dates + 19000000]
        return np.array(dates)

    @staticmethod
    def get_main_parameters_by_path(cod_file_path):
        _, _, season = os.path.basename(cod_file_path).split('_')
        p = os.path.dirname(os.path.dirname(cod_file_path))
        predictand = os.path.basename(p)
        p = os.path.dirname(p)
        region_type = os.path.basename(p)
        p = os.path.dirname(p)
        fields = os.path.basename(p).split('_')
        if len(fields) == 2:
            model, scenario = fields
        else:
            model, scenario = fields[0], ''

        return MainParameters(model, scenario, region_type, season, predictand)

    @staticmethod
    def get_modsce(model, scenario):
        if model in ['NNR', 'AWAP'] or scenario in [None, '', 'VALID']:
            return model
        else:
            return model + '_' + scenario

    def get_dirout(self, model, scenario, region_type, season, predictand):
        return os.path.join(self.base_dir or os.getcwd(),
                            CoD.get_modsce(model, scenario),
                            region_type,
                            predictand,
                            'season_%s' % season)

    def get_cod_file_path(self, main_parameters):
        """

        :param main_parameters:
        :type main_parameters: parameters.MainParameters
        :return:
        :rtype:
        """
        cod_file_path = os.path.join(self.base_dir, main_parameters.get_dirout(),
                                     'rawfield_analog_%s' % main_parameters.season)
        return cod_file_path

    @staticmethod
    def read_from_file(cod_file_path):
        """ Read from the given CoD file path
        """
        with open(cod_file_path) as ins:
            _, _, season = ins.readline().split()
            rdates = []
            adates = []
            edists = []
            for line in ins.readlines():
                if line.strip() != '':
                    fields = line.split()
                    rdates.append(fields[0])
                    adates.append(fields[1])
                    edists.append(fields[2])

        return {
            'rdates': np.array(rdates, dtype=int),
            'adates': np.array(adates, dtype=int),
            'edists': np.array(edists, dtype=float),
        }

    def read(self, main_parameters):
        """ Given the model, scenario, region_type, season, predictand, locate the CoD file path and read its content
        """
        return CoD.read_from_file(self.get_cod_file_path(main_parameters))
