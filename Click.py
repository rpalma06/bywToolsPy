class Click:

    def __init__(self, _frame, _tool, _x, _y):
        self._frame = 0
        self._tool = 0
        self._x = 0.0
        self._y = 0.0

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, value):
        self._frame = value

    @property
    def tool(self):
        return self._tool

    @tool.setter
    def tool(self, new_tool):
        self._tool = new_tool

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        self._x = new_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        self._y = new_y

