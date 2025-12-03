from math import sqrt, sin, cos, atan2, isclose
import numbers

support_type = (tuple, list)

def make_sure_is_num(x, y):
    if not isinstance(x, numbers.Real): 
        raise TypeError(f"Invalid number at index 0: value={x!r}, type={type(x)}")
    if not isinstance(y, numbers.Real): 
        raise TypeError(f"Invalid number at index 1: value={y!r}, type={type(y)}")
    return (x, y)

def get_support_pair(value, no_zero: bool = False):
    if isinstance(value, Vector): 
        pair = value
    elif isinstance(value, (int, float)): 
        pair = Vector(value, value)
    elif isinstance(value, support_type) and len(value) == 2: 
        pair = Vector(*make_sure_is_num(value[0], value[1]))
    elif isinstance(value, dict):
        if len(value) != 1: raise TypeError("字典必須只有一組鍵值")
        key = next(iter(value))
        pair = Vector(*make_sure_is_num(key, value[key]))
    else: 
        return None
    if no_zero and (pair.x == 0 or pair.y == 0):
        raise ZeroDivisionError("division by zero in vector component")
    return pair

# min max sum divmod round enumerate bool
class Vector:
    __slots__ = ("x", "y")
    def __init__(self, *args):
        """接受 Vector, -x, y- , tuple, list"""
        if len(args) == 0: 
            self.x: int = 0
            self.y: int = 0
        if len(args) == 1:
            value = args[0]
            if isinstance(value, Vector): self.x, self.y = value.x, value.y
            elif isinstance(value, support_type) and len(value) == 2:
                self.x, self.y = value
            else:
                try: self.x, self.y = value
                except: raise TypeError("Invalid single argument for Vector")
        elif len(args) == 2: self.x, self.y = args
        else: raise TypeError("Invalid arguments for Vector initialization")
        make_sure_is_num(self.x, self.y)

    @property
    def pair(self) -> tuple: return (self.x, self.y)
    @property
    def width(self): return self.x
    @property
    def height(self): return self.y

    # 常用方法
    def to_int(self) -> "Vector":
        """回傳取整數的新向量"""
        return Vector(int(self.x), int(self.y))
    def length_squared(self):
        """回傳長度平方"""
        return self.x**2 + self.y**2
    def length(self):
        """回傳向量長度"""
        return sqrt(self.length_squared())
    def normalize(self) -> "Vector":
        """回傳單位向量"""
        if not self: return Vector(0, 0)
        len_ = self.length()
        return Vector(self.x / len_, self.y / len_)
    def angle(self):
        """回傳角度 (弧度)"""
        return atan2(self.y, self.x)
    def near(self, other: "Vector", max_dist: int|float = 1):
        """判斷與另一向量是否在 max_dist 範圍內"""
        rel_vec = abs(self-other)
        return (rel_vec.x <= max_dist) and (rel_vec.y <= max_dist)
    def rotate(self, angle_rad: float) -> "Vector":
        """以弧度旋轉"""
        c, s = cos(angle_rad), sin(angle_rad)
        return Vector(self.x * c - self.y * s, self.x * s + self.y * c)
    def dist(self, other: "Vector"):
        return (self-other).length()
    def lerp(self, other: "Vector", t: float) -> "Vector":
        """線性插值 (0<=t<=1)"""
        return self * (1 - t) + other * t
    def copy(self) -> "Vector": return Vector(self.x, self.y)

    # 運算子
    def __neg__(self) -> "Vector":
        """operator -self"""
        return Vector(-self.x, -self.y)

    def __add__(self, other):
        """operator self + other"""
        pair = get_support_pair(other)
        return NotImplemented if pair is None else Vector(self.x + pair.x, self.y + pair.y)
    def __radd__(self, other):
        """operator other + self"""
        return self.__add__(other)

    def __sub__(self, other):
        """operator self - other"""
        pair = get_support_pair(other)
        return NotImplemented if pair is None else Vector(self.x - pair.x, self.y - pair.y)
    def __rsub__(self, other):
        """operator other - self"""
        pair = get_support_pair(other)
        return NotImplemented if pair is None else Vector(pair.x - self.x, pair.y - self.y)

    def __mul__(self, other):
        """operator self * other"""
        pair = get_support_pair(other)
        return NotImplemented if pair is None else Vector(self.x * pair.x, self.y * pair.y)
    def __rmul__(self, other):
        """operator other * self"""
        return self.__mul__(other)

    def __truediv__(self, other):
        """operator self / other"""
        pair = get_support_pair(other, no_zero=True)
        return NotImplemented if pair is None else Vector(self.x / pair.x, self.y / pair.y)
    def __rtruediv__(self, other):
        """operator other / self"""
        pair = get_support_pair(other, no_zero=True)
        return NotImplemented if pair is None else Vector(pair.x / self.x, pair.y / self.y)

    def __floordiv__(self, other):
        """operator self // other"""
        pair = get_support_pair(other, no_zero=True)
        return NotImplemented if pair is None else Vector(self.x // pair.x, self.y // pair.y)
    def __rfloordiv__(self, other):
        """operator other // self"""
        pair = get_support_pair(other, no_zero=True)
        return NotImplemented if pair is None else Vector(pair.x // self.x, pair.y // self.y)

    def __mod__(self, other):
        pair = get_support_pair(other, no_zero=True)
        return NotImplemented if pair is None else Vector(self.x % pair.x, self.y % pair.y)
    def __rmod__(self, other):
        pair = get_support_pair(other, no_zero=True)
        return NotImplemented if pair is None else Vector(pair.x % self.x, pair.y % self.y)

    # in-place 運算
    def __iadd__(self, other):
        """operator self += other"""
        pair = get_support_pair(other)
        if pair is None: raise TypeError(f"Unsupported type for Vector: {type(other)}")
        self.x += pair.x; self.y += pair.y
        return self
    def __isub__(self, other):
        """operator self -= other"""
        pair = get_support_pair(other)
        if pair is None: raise TypeError(f"Unsupported type for Vector: {type(other)}")
        self.x -= pair.x; self.y -= pair.y
        return self
    def __imul__(self, other):
        """operator self *= other"""
        pair = get_support_pair(other)
        if pair is None: raise TypeError(f"Unsupported type for Vector: {type(other)}")
        self.x *= pair.x; self.y *= pair.y
        return self
    def __itruediv__(self, other):
        """operator self /= other"""
        pair = get_support_pair(other, no_zero=True)
        if pair is None: raise TypeError(f"Unsupported type for Vector: {type(other)}")
        self.x /= pair.x; self.y /= pair.y
        return self
    def __ifloordiv__(self, other):
        """operator self //= other"""
        pair = get_support_pair(other, no_zero=True)
        if pair is None: raise TypeError(f"Unsupported type for Vector: {type(other)}")
        self.x //= pair.x; self.y //= pair.y
        return self

    # 其他
    def __getitem__(self, index: int) -> int|float:
        """索引[] -2~1"""
        if isinstance(index, slice): return (self.x, self.y)[index]
        if index in (0, -2): return self.x
        if index in (1, -1): return self.y
        raise IndexError(f"Vector index out of range: {index}")

    def __bool__(self): return (self.x != 0 and self.y != 0)

    def __repr__(self) -> str:
        """物件字串 (調試用)"""
        return f"Vector(x={self.x}, y={self.y})"
    __str__ = __repr__

    def __eq__(self, other) -> bool:
        pair = get_support_pair(other)
        if pair is None: return False
        return isclose(self.x, pair.x, rel_tol=1e-9, abs_tol=1e-12) and \
            isclose(self.y, pair.y, rel_tol=1e-9, abs_tol=1e-12)
    
    def __ne__(self, other) -> bool:
        """operator self != other"""
        return not self.__eq__(other)

    def __abs__(self):
        """abs(self)"""
        return Vector(abs(self.x), abs(self.y))
    
    def __hash__(self):
        """允許用於集合與字典 key"""
        return hash(self.pair)
    
    def __iter__(self):
        """允許拆包 (for 迴圈或 tuple)"""
        yield self.x
        yield self.y

    def __round__(self, ndigits=None):
        return Vector(*(round(x, ndigits) for x in self.pair))

    def __divmod__(self, other):
        if isinstance(other, (int, float)):
            q = [x // other for x in self.pair]
            r = [x % other for x in self.pair]
            return Vector(*q), Vector(*r)
        raise TypeError("divmod only supports scalar division")



class Circle:
    def __init__(self, center: Vector, radius: float):
        # Circle(center: Vector, radius: float)
        self.center = center
        self.radius = radius

    def rel_vector(self, point: Vector) -> Vector:
        return (point - self.center)

    def in_circle(self, point: Vector) -> bool:
        """判斷點是否在圓內(含邊界)"""
        dist = self.rel_vector(point).length()
        return dist <= self.radius

    def __repr__(self):
        return f"Circle(center={self.center}, radius={self.radius})"

    def copy(self) -> "Circle":
        """回傳複製品"""
        return Circle(self.center, self.radius)
