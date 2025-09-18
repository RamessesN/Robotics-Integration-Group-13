markers = []
target_info: str | None = None

class MarkerInfo:
    def __init__(self, x, y, w, h, info, width = 640, height = 360):
        self._x, self._y, self._w, self._h, self._info = x, y, w, h, info
        self.width = width
        self.height = height

    @property
    def info(self):
        """Return the Marker Itself"""
        return self._info

    @property
    def pt1(self):
        """Top-Left Coordinate"""
        return int((self._x - self._w / 2) * self.width), int((self._y - self._h / 2) * self.height)

    @property
    def pt2(self):
        """Bottom-Right Coordinate"""
        return int((self._x + self._w / 2) * self.width), int((self._y + self._h / 2) * self.height)

    @property
    def area(self):
        """Area of the Marker"""
        w_pix = self._w * self.width
        h_pix = self._h * self.height
        return int(w_pix * h_pix)

    @property
    def center(self):
        """Center Coordinate of the Marker"""
        x1, y1 = self.pt1
        x2, y2 = self.pt2
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

def sub_data_handler_vision(sub_info):
    """
    Callback function to receive data from the vision module
    :param sub_info: markers from the view
    """
    global markers
    markers.clear()
    for x, y, w, h, info in sub_info:
        marker = MarkerInfo(x, y, w, h, info)
        markers.append(marker)

def get_specified_marker(target: str | None):
    if target is None:
        return None
    for marker in markers:
        if marker.info == target:
            return marker
    return None