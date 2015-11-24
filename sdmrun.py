#!/usr/bin/env python
"""
Command line interface to the Statistical Downscaling Model (SDM) package.
"""
import os
import sys
import logging
from ConfigParser import ConfigParser
import argparse

from sdm import __version__
from sdm.cod import CoD
from sdm.gridded import Data2DReader
from sdm.extractor import GriddedExtractor
from sdm.parameters import MainParameters
from sdm.mask import MaskReader

logging.basicConfig(level=logging.WARNING)


def read_config(config_file):
    if not config_file:
        if 'USERPROFILE' in os.environ:  # Windows
            config_file = os.path.join(os.environ['USERPROFILE'], '.sdm.cfg')
        else:
            config_file = os.path.join(os.environ['HOME'], '.sdm.cfg')

    config = ConfigParser()
    config.optionxform = str  # preserve case
    config.read(config_file)

    return config


def main(args):
    ap = argparse.ArgumentParser(prog=os.path.basename(__file__),
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='',
                                 epilog=__doc__)

    ap.add_argument('-c', '--config-file',
                    required=False,
                    help='the configuration file, default to "$HOME/.sdm.cfg"')
    ap.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help='be more chatty')
    ap.add_argument('-V', '--version',
                    action='version',
                    version='%s: v%s' % (ap.prog, __version__))

    subparsers = ap.add_subparsers(dest='sub_command',
                                   title='List of sub-commands',
                                   metavar='sub-command',
                                   help='"%s sub-command -h" for more help' % ap.prog)

    cod_getpath_parser = subparsers.add_parser('cod-getpath',
                                               help='get the full path to a CoD file')

    cod_getpath_parser.add_argument('-m', '--model',
                                    required=True,
                                    help='model name')
    cod_getpath_parser.add_argument('-c', '--scenario',
                                    required=False,
                                    help='scenario name, e.g. historical, rcp45, rcp85')
    cod_getpath_parser.add_argument('-r', '--region-type',
                                    required=True,
                                    help='pre-defined region type name, e.g. sea, sec, tas ...')
    cod_getpath_parser.add_argument('-s', '--season',
                                    required=True,
                                    help='season number, e.g. 1 (DJF), 2 (MAM), 3 (JJA), or 4 (SON)')
    cod_getpath_parser.add_argument('-p', '--predictand',
                                    required=True,
                                    help='predictand name, e.g. rain, tmax, tmin')

    dxt_gridded_parser = subparsers.add_parser('dxt-gridded',
                                               help='extract gridded data using the given cod file')
    dxt_gridded_parser.add_argument('cod_file_path',
                                    help='full path to the CoD file')
    dxt_gridded_parser.add_argument('output_file',
                                    help='output netCDF file name')
    dxt_gridded_parser.add_argument('-R', '--region',
                                    required=False,
                                    help='the region where the data are to be extracted')

    dxt_gridded2_parser = subparsers.add_parser('dxt-gridded2',
                                                help='extract gridded data with the given parameters')
    dxt_gridded2_parser.add_argument('output_file',
                                     help='output netCDF file name')
    dxt_gridded2_parser.add_argument('-m', '--model',
                                     required=True,
                                     help='model name')
    dxt_gridded2_parser.add_argument('-c', '--scenario',
                                     required=False,
                                     help='scenario name, e.g. historical, rcp45, rcp85')
    dxt_gridded2_parser.add_argument('-r', '--region-type',
                                     required=True,
                                     help='pre-defined region type name, e.g. sea, sec, tas ...')
    dxt_gridded2_parser.add_argument('-s', '--season',
                                     required=True,
                                     help='season number, e.g. 1 (DJF), 2 (MAM), 3 (JJA), or 4 (SON)')
    dxt_gridded2_parser.add_argument('-p', '--predictand',
                                     required=True,
                                     help='predictand name, e.g. rain, tmax, tmin')
    dxt_gridded2_parser.add_argument('-R', '--region',
                                     required=False,
                                     help='the region where the data are to be extracted (default to region-type)')


    to_3d_parser = subparsers.add_parser('to-3d',
                                         help='Convert and save the 2D (dates, gpnames) file to 3D (dates, lat, lon)')
    to_3d_parser.add_argument('data2d_file',
                              help='The input file containing the 2D data')
    to_3d_parser.add_argument('data3d_file',
                              help='The output file')

    ns = ap.parse_args(args)

    config = read_config(ns.config_file)

    if ns.sub_command == 'cod-getpath':
        main_parameters = MainParameters(ns.model, ns.scenario, ns.region_type, ns.season, ns.predictand)
        print CoD(config.get('dxt', 'cod_base_dir')).get_cod_file_path(main_parameters)

    elif ns.sub_command in ('dxt-gridded', 'dxt-gridded2'):
        gridded_extractor = GriddedExtractor(cod_base_dir=config.get('dxt', 'cod_base_dir'),
                                             mask_base_dir=config.get('dxt', 'mask_base_dir'),
                                             gridded_base_dir=config.get('dxt', 'gridded_base_dir'))

        if ns.sub_command == 'dxt-gridded':
            main_parameters = MainParameters.from_filepath(ns.cod_file_path)
        else:
            main_parameters = MainParameters(ns.model, ns.scenario, ns.region_type, ns.season, ns.predictand)

        data = gridded_extractor.extract(main_parameters, ns.region)

        data.save_nc(ns.output_file, main_parameters)

    elif ns.sub_command == 'to-3d':
        main_parameters = MainParameters.from_filepath(ns.data2d_file)
        data2d = Data2DReader().read(ns.data2d_file)
        mask_reader = MaskReader(base_dir=config.get('dxt', 'mask_base_dir'))
        mask = mask_reader.read(main_parameters.region_type)
        data3d = data2d.to_3d(mask.crop())

        data3d.save_nc(ns.data3d_file, main_parameters=main_parameters)




if __name__ == '__main__':
    main(sys.argv[1:])

