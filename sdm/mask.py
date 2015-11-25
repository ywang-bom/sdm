import os
from collections import namedtuple
import logging

import numpy as np
from scipy.io import netcdf

MaskBase = namedtuple('MaskBase', 'data, lat, lon')


class Mask(MaskBase):
    def __new__(cls, *args, **kwargs):
        self = super(Mask, cls).__new__(cls, *args, **kwargs)

        # Additional initialization for the mask
        self._idx_mask_2d = np.where(self.data != 0)
        self._idx_mask_flat = np.ravel_multi_index(self._idx_mask_2d, self.data.shape)
        lon = (self.lon[self._idx_mask_2d[1]] * 100).astype(long) * 10000
        lat = (self.lat[self._idx_mask_2d[0]] * -100).astype(long)
        self._gpnames = lon + lat

        return self

    @property
    def idx_mask_2d(self):
        """
        The 2D indices to the mask.
        :return: A 2-element tuple with each element as indices to one of the dimension
        :rtype: tuple
        """
        return self._idx_mask_2d

    @property
    def idx_mask_flat(self):
        """
        The flat indices to the mask as if it is a vector
        """
        return self._idx_mask_flat

    @property
    def gpnames(self):
        """
        Calculate an array of gpnames from the mask
        """
        return self._gpnames

    def crop(self):
        """
        Crop the mask so that there is no effetive mask area is tightly bound.
        :return:
        :rtype:
        """
        idx_lat_min = np.min(self.idx_mask_2d[0])
        idx_lat_max = np.max(self.idx_mask_2d[0]) + 1
        idx_lon_min = np.min(self.idx_mask_2d[1])
        idx_lon_max = np.max(self.idx_mask_2d[1]) + 1

        lat_subsetted = self.lat[idx_lat_min: idx_lat_max]
        lon_subsetted = self.lon[idx_lon_min: idx_lon_max]
        data_subsetted = self.data[idx_lat_min: idx_lat_max, idx_lon_min: idx_lon_max]

        return Mask(data_subsetted, lat_subsetted, lon_subsetted)


class MaskReader(object):
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.getcwd()

    def read(self, region_name):
        file_path = os.path.join(self.base_dir, 'mask_%s.nc' % region_name)
        logging.debug('reading mask file: {}'.format(file_path))
        ncd_file = netcdf.netcdf_file(file_path)

        try:
            mask = Mask(ncd_file.variables['mask'].data.copy(),
                        ncd_file.variables['lat'].data.copy(),
                        ncd_file.variables['lon'].data.copy())
        finally:
            ncd_file.close()

        return mask

