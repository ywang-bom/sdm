import os
from collections import namedtuple

_MAIN_PARAMETER_MEMBERS = 'model scenario region_type season predictand region'

_MainParametersBase = namedtuple('_MainParametersBase', _MAIN_PARAMETER_MEMBERS)


def get_modsce(model, scenario):
    if model in ['NNR', 'AWAP'] or scenario in [None, '', 'VALID']:
        return model
    else:
        return model + '_' + scenario


class MainParameters(_MainParametersBase):
    def __new__(cls, *args, **kwargs):

        if not (len(args) >= 6 or 'region' in kwargs):
            if len(args) >= 3:
                kwargs['region'] = args[2]
            elif 'region_type' in kwargs:
                kwargs['region'] = kwargs['region_type']

        self = super(MainParameters, cls).__new__(cls, *args, **kwargs)

        return self

    def __str__(self):
        return '{}, {}, {}, {}, {}'.format(self.model,
                                           self.scenario,
                                           self.region_type,
                                           self.season,
                                           self.predictand)

    @staticmethod
    def from_filepath(filepath):
        s = os.path.dirname(filepath)
        season = os.path.basename(s)
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

        return MainParameters(model, scenario, region_type, season, predictand)

    def get_modsce(self):
        return get_modsce(self.model, self.scenario)

    def get_dirout(self):
        return os.path.join(self.get_modsce(),
                            self.region_type,
                            self.predictand,
                            'season_{}'.format(self.season))

    def get_ds_file(self):
        return os.path.join(self.get_dirout(), 'ds_grid_data_{}.nc'.format(self.season))

    def get_var_code(self):
        return self.predictand if self.predictand != 'rain' else 'rr'
