import freenect as fn
import time as t
import math
import numpy as np

SAMPLE_DISTANCE = 16

SENSOR_MAX_DEPTH = 4.
SENSOR_PIXEL_HEIGHT = 480
SENSOR_PIXEL_WIDTH = 640
SENSOR_ANGULAR_WIDTH = math.radians(57.);
SENSOR_ANGULAR_HEIGHT = math.radians(43.)
SENSOR_ANGULAR_ELEVATION = math.radians(0.)


class KinGeo:
    """
    Class handling usage of Kinect input and data processing
    to produce point cloud and geometry

    Supports a single Kinect in use
    """
    kinect_initialized = False

    def __init__(self):
        self.last_access = 0.  # time of last kinect depth map access
        self._frame_time = 1./30.  # float of min time in seconds per frame
        self._depth_arr = None  # holds numpy array of
        self._pc_timestamp = 0.

        if not KinGeo.kinect_initialized:
            fn.init()
            KinGeo.kinect_initialized = True

    @property
    def t_since_last_frame(self):
        """
        Returns time since last depth frame was accessed from Kinect
        :return: float
        """
        return t.time() - self.last_access

    @property
    def access_hz(self):
        """
        Gets access Hz of kinect. Will not ask the Kinect for depth
        data more often than this.
        :return: float
        """
        return 1. / self._frame_time

    @access_hz.setter
    def access_hz(self, hz):
        """
        Sets maximum rate at which KinGeo will ask Kinect for depth info
        :return: None
        """
        self._frame_time = 1. / float(hz)

    @property
    def depth_map(self):
        """
        Gets depth map as numpy array.
        :return: np.Array
        """
        if self.t_since_last_frame > self._frame_time:
            self._depth_arr = fn.sync_get_depth()
        return self._depth_arr[0]  # gets depth map from first Kinect found

    @property
    def points_arr(self):
        """
        Gets point cloud of positions from depth map
        :return: np.Array
        """
        dm = self.depth_map
        positions = []
        half_px_width = SENSOR_PIXEL_WIDTH / 2
        half_px_height = SENSOR_PIXEL_HEIGHT / 2
        for x in range(0, SENSOR_PIXEL_WIDTH, SAMPLE_DISTANCE):
            for y in range(0, SENSOR_PIXEL_HEIGHT, SAMPLE_DISTANCE):
                depth = float(dm[0][y]) / 2048. * SENSOR_MAX_DEPTH
                if depth == 2047:
                    continue  # if depth is max value, ignore it.
                angularX = (x - half_px_width) / SENSOR_PIXEL_WIDTH * \
                    SENSOR_ANGULAR_WIDTH
                angularY = (y - half_px_height) / SENSOR_PIXEL_HEIGHT * \
                    SENSOR_ANGULAR_HEIGHT + SENSOR_ANGULAR_ELEVATION
                pos = np.array((
                    math.sin(angularX) * depth,
                    math.sin(angularY) * depth,
                    math.cos(angularX) * math.cos(angularY) * depth
                )).astype(np.float32)
                positions.append(pos)  # this is terrible for performance
        return np.array(positions)  # .astype(np.float32)

if __name__ == '__main__':
    kin_geo = KinGeo()  # create kinect handler obj
    dm = kin_geo.depth_map
    print(len(dm))
    print(len(dm[0]))
    print(len(dm[0][0]))
    print(dm[1])
