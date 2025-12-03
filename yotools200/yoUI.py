import pygame
from . import colors
from .Game_2D import Vector
from yoCppVec.Game_2D import CppVec
from .utils import resource_path, true_func, empty_func
from typing import Callable
from math import atan2, cos, sin, degrees

pygame.init()
pygame.font.init()

'''向右=0 逆時針為正'''
_already_init: bool = False
_font_cache: dict[tuple[str, int], pygame.font.Font]
_image_cache: dict[str, pygame.Surface]
mandarin = "DFKai-SB"

def _make_sure_init():
    if not _already_init: raise RuntimeError("pygame_tools hadn't init yet")

def yoUI_init():
    global _font_cache, _already_init, _image_cache
    if _already_init: raise RuntimeError("pygame_tools had already init")
    _font_cache = {}
    _image_cache = {}
    _already_init = True

def get_font(name: str, size: int) -> pygame.font.Font:
    """ 字體快取 """
    _make_sure_init()
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size)
    return _font_cache[key]

def get_image(path: str) -> pygame.Surface:
    """ 圖片快取 """
    full_path = resource_path(path.replace("\\", "/"))
    if full_path not in _image_cache:
        _image_cache[full_path] = pygame.image.load(full_path).convert_alpha()
    return _image_cache[full_path]

def yoUI_clear_cache():
    _font_cache.clear()
    _image_cache.clear()

class yoDraw:
    def __init__(self, screen: pygame.Surface) -> None:
        """ 
        單純畫圖/沒有互動的靜態UI 
        使用絕對座標 視窗大小固定
        """
        _make_sure_init()
        self.screen: pygame.Surface = screen
        self.screen_size = Vector(self.screen.get_size())

    @staticmethod
    def rotate_image(image: pygame.Surface, radian: float) -> pygame.Surface:
        """旋轉圖片 (向右為0 逆時針為正)"""
        angle_deg = -degrees(radian) - 90 # 圖片原始向上 轉成向右為0
        return pygame.transform.rotate(image, angle_deg)

    def blit(self, image: pygame.Surface, pos: Vector, alpha: int|None = None, align: str = "topleft"):
        # 透明度
        if alpha is not None: image.set_alpha(alpha) 
        else: image.convert_alpha()
        # 顯示圖片
        rect = image.get_rect(**{align: pos.pair})
        self.screen.blit(image, rect)

    def text(self, size: int, word, color: tuple, pos: Vector, alpha: int = 255, 
            _font: str = "", align: str = "topleft", back_color: tuple|None = None) -> None:
        """ 顯示文字 """
        font = get_font(_font, size)
        text_surface = font.render(str(word), True, color, back_color).convert_alpha()
        # 設定透明度 (0~255)
        text_surface.set_alpha(alpha)  
        # 對齊座標
        rect = text_surface.get_rect(**{align: pos.pair})
        self.screen.blit(text_surface, rect)

    def image(self, path: str, scale: float|int|Vector = 1, pos: Vector|None = None, 
              alpha: int|None = None, align: str = "topleft") -> pygame.Surface:
        """建立調整過大小的圖片 如果沒傳入 pos 則不顯示"""
        image = get_image(path)
        # 根據型別判斷image_size
        image_size = scale.pair if isinstance(scale, Vector) else tuple(x*scale for x in image.get_size())
        image = pygame.transform.scale(image, image_size)
        if pos is None:
            # 透明度
            if alpha is not None: image.set_alpha(alpha) 
            else: image.convert_alpha()
            return image
        self.blit(image, pos, alpha, align)
        return image

    def rect(self, topleft: Vector, size: Vector, color: tuple, width: int = 0):
        """ 繪製 Rect """
        pygame.draw.rect(self.screen, color, (*topleft.pair, *size.pair), width)

    def circle(self, center: Vector, radius: int|float, color: tuple, width: int = 0):
        """根據參數繪製 Circle 物件"""
        pygame.draw.circle(self.screen, color, center.pair, radius, width)
    
    def sector(self, center: Vector, radius: float, 
                    central_radian: float, radian_range: float, 
                    color: tuple[int, int, int] = colors.white, 
                    width: int = 0, segments: int = 60):
        """
        繪製扇形 (中心弧度 ± 範圍)
        Args:
            center (Vector): 扇形中心
            central_radian (float): 中心方向 (向上為 0)
            radian_range (float): 扇形擴張角度(正負範圍)
            radius (float): 半徑
            color: 顏色
            width (int): 線寬(0 表示實心)
            segments (int): 折線段數(越多越平滑)
        """
        points = [center.pair]
        start_angle = central_radian - radian_range
        end_angle = central_radian + radian_range

        for i in range(segments + 1):
            t = i / segments
            angle = start_angle + (end_angle - start_angle) * t
            x = center.x + radius * cos(angle)
            y = center.y + radius * sin(angle)
            points.append((x, y))

        pygame.draw.polygon(self.screen, color, points, width)

    def arc(self, topleft: Vector, size: Vector, color: tuple[int, int, int], 
            start_angle: int|float, stop_angle: int|float, width: int = 1):
        rect = (topleft.x, topleft.y, size.x, size.y)
        pygame.draw.arc(self.screen, color, rect, start_angle, stop_angle, width)

class yoButton:
    def __init__(self, screen: pygame.Surface, 
                 base_color: tuple[int, int, int], topleft: Vector, base_size: Vector, 
                 pressed_color: tuple[int, int, int]|None = None) -> None:
        _make_sure_init()
        self.screen = screen
        self.base_color = base_color
        self.pressed_color = pressed_color if (pressed_color is not None) else base_color
        self.base_rect = pygame.Rect(*topleft.pair, *base_size.pair)
        self.topleft = topleft
        self.base_size = base_size
    
    def is_pressed(self) -> bool:
        """ 檢查是否按下 """
        return self.base_rect.collidepoint(yoUI.get_mouse_pos().pair)
    
    def draw(self) -> None:
        color = self.pressed_color if self.is_pressed() else self.base_color
        pygame.draw.rect(self.screen, color, self.base_rect)

class yoTextButton(yoButton):
    def __init__(self, screen: pygame.Surface, 
                 base_color: tuple[int, int, int], topleft: Vector, base_size: Vector, 
                 text: str, text_color: tuple, text_size: int, text_offset: Vector = Vector(3, 3), 
                 pressed_color: tuple[int, int, int]|None = None) -> None:
        super().__init__(screen, base_color, topleft, base_size, pressed_color)
        self.text = text
        self.text_color = text_color
        self.text_size = text_size
        self.text_offset = text_offset
    
    def draw(self) -> None:
        super().draw()
        yoDraw(self.screen).text(self.text_size, self.text, self.text_color, self.topleft+self.text_offset)

class yoImageButton(yoButton):
    def __init__(self, screen: pygame.Surface, 
                 base_color: tuple[int, int, int], topleft: Vector, base_size: Vector, 
                 image_path: str, image_topleft: Vector = Vector(0, 0), 
                 pressed_color: tuple[int, int, int]|None = None) -> None:
        super().__init__(screen, base_color, topleft, base_size, pressed_color)
        self.image_path = image_path
        self.image_topleft = image_topleft
    
    def draw(self) -> None:
        super().draw()
        yoDraw(self.screen).image(self.image_path, self.base_size, self.topleft)

class yoJoystick:
    def __init__(self, screen: pygame.Surface) -> None:
        _make_sure_init()
        self.screen = screen

    def static_joystick(self, center: Vector, 
                        base_color: tuple[int, int, int] = colors.dark_blue, stick_style = None, 
                        base_radius: int = 50, stick_radius: int = 20, stick_pos: Vector|None = None
                        ):
        """
        繪製靜態搖桿 (不包含互動邏輯)
        Args:
            center (Vector): 搖桿底座中心座標
            base_color (tuple[int, int, int], optional): 搖桿底座顏色 預設為深藍色
            stick_style (Surface or color, optional): 
                若為 pygame.Surface 會將圖片縮放後作為搖桿手把；
                若為顏色 tuple 則畫圓作為手把；
                若為 None 預設使用藍色圓形手把。
            base_radius (int): 底座半徑
            stick_radius (int): 手把半徑
            stick_pos (Vector, optional): 手把座標 預設與中心相同
        """
        stick_center = stick_pos or center  # 沒提供 stick_pos 就用中心
        pygame.draw.circle(self.screen, base_color, center.pair, base_radius)
        if isinstance(stick_style, pygame.Surface):
            # 手把是圖片
            pic = stick_style.convert_alpha()
            side_len = stick_radius * 2
            scaled = pygame.transform.smoothscale(pic, (side_len, side_len))
            rect = scaled.get_rect(center=stick_center.pair)
            self.screen.blit(scaled, rect)
            return
        # 手把是color
        color = stick_style if stick_style else colors.blue
        pygame.draw.circle(self.screen, color, stick_center.pair, stick_radius)

    def drag_radian(self, stick_radius: int, 
                    action: Callable = empty_func, 
                    drag_start: list[None|Vector]|None = None,
                    *args, 
                    is_trigger_area: Callable[[Vector], bool] = true_func
                    ) -> tuple[None|Vector, Vector]:
        """
        傳入 drag_start 為 list 例如 [None] 或 [Vector(...)]
        回傳 (起始點, 相對向量)
        - 若沒觸發 回傳 (None, Vector(0, 0))
        """
        if drag_start == None: drag_start = [None]
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = Vector(pygame.mouse.get_pos())

        if mouse_pressed:
            # 尚未開始拖曳 檢查是否在觸發區
            if drag_start[0] is None:
                if not is_trigger_area(mouse_pos):
                    # 滑鼠沒在觸發區 什麼都不做
                    return None, Vector(0, 0)
                
                # 開始拖曳 記錄起始點
                drag_start[0] = mouse_pos
                # 剛開始拖曳 回傳起始點與零向量
                return mouse_pos, Vector(0, 0)

            # 拖曳進行中 回傳起始點與目前偏移量
            rel_vector: Vector = mouse_pos - drag_start[0]
            return drag_start[0], rel_vector

        # 滑鼠已放開 若有 (拖曳過且沒收回) 則觸發 action
        if isinstance(drag_start[0], Vector):
            rel_vector = mouse_pos - drag_start[0]
            if stick_radius <= rel_vector.length_squared() or rel_vector.length_squared() <= 5:
                action(*args) if args else action()

        # 歸零拖曳狀態
        drag_start[0] = None
        return None, Vector(0, 0)

    def joystick(self, center: Vector,
                base_color: tuple = colors.dark_blue,
                stick_style=colors.blue,
                base_radius: int = 50,
                stick_radius: int = 20,
                follow: bool = True,
                action: Callable = empty_func,
                drag_start: list = [None],
                *args,
                is_in_area: Callable[[Vector], bool] = true_func
                ) -> tuple[float|None, str]:
        
        start_pos, offset = self.drag_radian(stick_radius, action, drag_start, *args, is_trigger_area=is_in_area)

        if start_pos is None:
            self.static_joystick(center, base_color, stick_style, base_radius, stick_radius)
            return None, "none"  # 沒有觸發

        # 判斷是否按 or 拖動
        if offset.length() < 5:
            mode = "auto"
        else:
            mode = "drag"

        # 搖桿邏輯
        if follow:
            center = start_pos
        if offset.length() > base_radius:
            offset = offset.normalize() * (base_radius - stick_radius)
        stick_pos = center + offset
        self.static_joystick(center, base_color, stick_style, base_radius, stick_radius, stick_pos)

        radian = atan2(offset.y, offset.x)
        return radian, mode

class yoUI:
    def __init__(self, screen: pygame.Surface):
        _make_sure_init()
        self.screen = screen
        self.screen_size = Vector(screen.get_size())

        self.draw = yoDraw(screen)
        self.joystick = yoJoystick(screen)

    @staticmethod
    def image_collision(pic1: pygame.Surface, pic2: pygame.Surface, pos1: Vector, pos2: Vector) -> Vector | None:
        mask1 = pygame.mask.from_surface(pic1)
        mask2 = pygame.mask.from_surface(pic2)
        offset = (int(pos2.x - pos1.x), int(pos2.y - pos1.y))
        collision_point = mask1.overlap(mask2, offset)
        return Vector(pos1.x + collision_point[0], pos1.y + collision_point[1]) if collision_point else None

    @staticmethod
    def get_mouse_pos(index: int = 0) -> Vector:
        mouse_buttons = pygame.mouse.get_pressed()
        return Vector(pygame.mouse.get_pos()) if mouse_buttons[index] else Vector(-1, -1)

    def button(self, base_color: tuple[int, int, int], topleft: Vector, base_size: Vector, 
               pressed_color: tuple[int, int, int]|None = None) -> yoButton:
        return yoButton(self.screen, base_color, topleft, base_size, pressed_color)

    def text_button(self, base_color: tuple[int, int, int], topleft: Vector, base_size: Vector, 
                    text: str, text_color: tuple, text_size: int, text_offset: Vector = Vector(3, 3), 
                    pressed_color: tuple[int, int, int]|None = None) -> yoTextButton:
        return yoTextButton(self.screen, base_color, topleft, base_size, text, text_color, text_size, text_offset, pressed_color)

    def image_button(self, base_color: tuple[int, int, int], topleft: Vector, base_size: Vector, 
                     image_path: str, image_topleft: Vector = Vector(0, 0), 
                     pressed_color: tuple[int, int, int]|None = None) -> yoImageButton:
        return yoImageButton(self.screen, base_color, topleft, base_size, image_path, image_topleft, pressed_color)

    def abs(self, value: Vector) -> tuple[int, int]:
        return (int(self.screen_size.x / 100 * value.x), int(self.screen_size.y / 100 * value.y))

    def rel(self, value: Vector) -> tuple[int, int]:
        return (int(value.x / self.screen_size.x * 100), int(value.y / self.screen_size.y * 100))
