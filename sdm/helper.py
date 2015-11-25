import os
import logging

logger = logging.getLogger('helper')


def decompose_filepath(filepath):
    p = os.path.dirname(filepath)
    season = os.path.basename(p)
    p = os.path.dirname(os.path.dirname(filepath))
    predictand = os.path.basename(p)
    p = os.path.dirname(p)
    region_type = os.path.basename(p)
    p = os.path.dirname(p)
    fields = os.path.basename(p).split('_')
    if len(fields) == 2:
        model, scenario = fields
    else:
        model, scenario = fields[0], ''
    base_dir = os.path.dirname(p)

    logging.debug('\nbase_dir: {}\nmodel: {}\nscenario: {}\nregion_type: {}\nseason: {}\npredictand: {}\n'
                  .format(base_dir, model, scenario, region_type, season, predictand))

    return base_dir, (model, scenario, region_type, season, predictand)