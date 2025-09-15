markers = []
closest_marker = None

class MarkerInfo:
    def __init__(self, x, y, w, h, info, width = 640, height = 360):
        self._x, self._y, self._w, self._h, self._info = x, y, w, h, info
        self.width = width
        self.height = height

    @property
    def info(self):
        """返回自身"""
        return self._info

    @property
    def pt1(self):
        """左上角坐标"""
        return int((self._x - self._w / 2) * self.width), int((self._y - self._h / 2) * self.height)

    @property
    def pt2(self):
        """右下角坐标"""
        return int((self._x + self._w / 2) * self.width), int((self._y + self._h / 2) * self.height)

    @property
    def area(self):
        """marker面积"""
        w_pix = self._w * self.width
        h_pix = self._h * self.height
        return int(w_pix * h_pix)

    @property
    def center(self):
        """marker中心坐标"""
        x1, y1 = self.pt1
        x2, y2 = self.pt2
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

def sub_data_handler_vision(sub_info):
    """
    Callback function to receive data from the vision module
    :param sub_info: markers from the view
    """
    global markers, closest_marker
    markers.clear()
    closest_marker = None
    max_area = -1

    for x, y, w, h, info in sub_info:
        marker = MarkerInfo(x, y, w, h, info)
        markers.append(marker)
        if marker.area > max_area: # 选取最近的marker(基于面积)
            max_area = marker.area
            closest_marker = marker