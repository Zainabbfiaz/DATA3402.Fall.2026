import math
class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [[' '] * width for i in range(height)]

    def set_pixel(self, row, col, char='*'):
        self.data[row][col] = char

    def get_pixel(self, row, col):
        return self.data[row][col]

    def clear_canvas(self):
        self.data = [[' '] * self.width for i in range(self.height)]

    def v_line(self, x, y, h, **kargs):
        for i in range(x, x + h):
            self.set_pixel(i, y, **kargs)

    def h_line(self, x, y, w, **kargs):
        for i in range(y, y + w):
            self.set_pixel(x, i, **kargs)

    def line(self, x1, y1, x2, y2, **kargs):
        slope = (x2 - x1) / (y2 - y1)
        for y in range(y1, y2):
            x = x1 + int(slope * (y - y1))
            self.set_pixel(x, y, **kargs)

    def display(self):
        print("\n".join(["".join(row) for row in self.data]))


class Shape:
    def __init__(self, x, y):
        self._x = x  
        self._y = y  

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def area(self):
        raise NotImplementedError("Subclass must implement area()")

    def perimeter(self):
        raise NotImplementedError("Subclass must implement perimeter()")

    def perimeter_points(self):
        raise NotImplementedError("Subclass must implement perimeter_points()")

    def contains_point(self, px, py):
        raise NotImplementedError("Subclass must implement contains_point()")

    def overlaps(self, other):
        if self.contains_point(other.get_x(), other.get_y()):
            return True
        if other.contains_point(self._x, self._y):
            return True
        for (px, py) in self.perimeter_points():
            if other.contains_point(px, py):
                return True
        for (px, py) in other.perimeter_points():
            if self.contains_point(px, py):
                return True
        return False

    def paint(self, canvas, char='*'):
        for (px, py) in self.perimeter_points():
            row, col = int(round(px)), int(round(py))
            if 0 <= row < canvas.height and 0 <= col < canvas.width:
                canvas.set_pixel(row, col, char)

    def _points_on_polygon(self, vertices, num_points=16):
        n_edges = len(vertices)
        base = num_points // n_edges
        extra = num_points % n_edges

        points = []
        for i in range(n_edges):
            x0, y0 = vertices[i]
            x1, y1 = vertices[(i + 1) % n_edges]
            n_this_edge = base + (1 if i < extra else 0)
            for k in range(n_this_edge):
                t = k / n_this_edge
                px = x0 + t * (x1 - x0)
                py = y0 + t * (y1 - y0)
                points.append((px, py))
        return points


class Rectangle(Shape):
    def __init__(self, length, width, x, y):
        super().__init__(x, y)
        self.__length = length
        self.__width = width

    def get_length(self):
        return self.__length

    def get_width(self):
        return self.__width

    def area(self):
        return self.__length * self.__width

    def perimeter(self):
        return 2 * (self.__length + self.__width)

    def perimeter_points(self):
        corners = [
            (self._x, self._y),
            (self._x + self.__length, self._y),
            (self._x + self.__length, self._y + self.__width),
            (self._x, self._y + self.__width),
        ]
        return self._points_on_polygon(corners, num_points=16)

    def contains_point(self, px, py):
        within_x = self._x <= px <= self._x + self.__length
        within_y = self._y <= py <= self._y + self.__width
        return within_x and within_y


class Circle(Shape):
    def __init__(self, radius, x, y):
        super().__init__(x, y)
        self.__radius = radius

    def get_radius(self):
        return self.__radius

    def area(self):
        return math.pi * self.__radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.__radius

    def perimeter_points(self):
        points = []
        num_points = 16
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            px = self._x + self.__radius * math.cos(angle)
            py = self._y + self.__radius * math.sin(angle)
            points.append((px, py))
        return points

    def contains_point(self, px, py):
        distance = math.sqrt((px - self._x) ** 2 + (py - self._y) ** 2)
        return distance <= self.__radius


class Triangle(Shape):
    def __init__(self, side_a, side_b, side_c, x, y):
        super().__init__(x, y)
        self.__side_a = side_a
        self.__side_b = side_b
        self.__side_c = side_c

    def get_side_a(self):
        return self.__side_a

    def get_side_b(self):
        return self.__side_b

    def get_side_c(self):
        return self.__side_c

    def area(self):
        a, b, c = self.__side_a, self.__side_b, self.__side_c
        s = (a + b + c) / 2
        return math.sqrt(s * (s - a) * (s - b) * (s - c))

    def perimeter(self):
        return self.__side_a + self.__side_b + self.__side_c

    def _vertices(self):
        a, b, c = self.__side_a, self.__side_b, self.__side_c
        vertex_a = (self._x, self._y)
        vertex_b = (self._x + c, self._y)
        angle_a = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
        vertex_c = (self._x + b * math.cos(angle_a), self._y + b * math.sin(angle_a))
        return [vertex_a, vertex_b, vertex_c]

    def perimeter_points(self):
        return self._points_on_polygon(self._vertices(), num_points=16)

    @staticmethod
    def _sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    def contains_point(self, px, py):
        v1, v2, v3 = self._vertices()
        pt = (px, py)
        d1 = self._sign(pt, v1, v2)
        d2 = self._sign(pt, v2, v3)
        d3 = self._sign(pt, v3, v1)
        has_negative = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_positive = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_negative and has_positive)


class CompoundShape(Shape):

    def __init__(self, shapes):
        if not shapes:
            raise ValueError("CompoundShape needs at least one shape")
        avg_x = sum(s.get_x() for s in shapes) / len(shapes)
        avg_y = sum(s.get_y() for s in shapes) / len(shapes)
        super().__init__(avg_x, avg_y)
        self.__shapes = list(shapes)

    def get_shapes(self):
        return list(self.__shapes)

    def area(self):
        return sum(s.area() for s in self.__shapes)

    def perimeter(self):
        return sum(s.perimeter() for s in self.__shapes)

    def perimeter_points(self):
        points = []
        for s in self.__shapes:
            points.extend(s.perimeter_points())
        return points

    def contains_point(self, px, py):
        return any(s.contains_point(px, py) for s in self.__shapes)

    def paint(self, canvas, char='*'):
        for s in self.__shapes:
            s.paint(canvas, char)
