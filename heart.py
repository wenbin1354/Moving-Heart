# encoding: utf-8
# this is a file that creates a bumping heart
import random
import time
from math import sin, cos, pi, log
from tkinter import *

CANVAS_WIDTH = 500  
CANVAS_HEIGHT = 360  
CANVAS_CENTER_X = CANVAS_WIDTH / 2  
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2 
IMAGE_ENLARGE = 11  
HEART_COLOR = "#e86184"  

WINDOWS_TITLE = 'heart'  


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    """
    :param shrink_ratio: 
    :param t: 
    :return: coord
    """

    # x = 16 * (sin(t) ** 3)
    x = 14.6 * (sin(t) ** 3)  # sharper
    # y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    y = -(14.5 * cos(t) - 4 * cos(2 * t) - 2 * cos(3 * t) - 0.5 * cos(4 * t))  # more round

    # enlarge
    x *= shrink_ratio
    y *= shrink_ratio

    # move to center
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    """
    :param x: 
    :param y: 
    :param beta: 
    :return: new coord
    """
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)

    return x - dx, y - dy


def shrink(x, y, ratio):
    """
    :param x: 
    :param y: 
    :param ratio: 
    :return: new coord
    """
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)  # 这个参数...
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def heart_curve(p):
    """
    :param p: 
    :return: 
    """
    return curve(p, (.69, .75, .2, .95)) 


def heart_halo_curve(p):
    """
    :param p: 
    :return: 
    """

    return curve(p, (.75, .49, .46, .97))  


def curve(p, b):
    """
    :param b: 
    :param p: 
    :return: 
    """


    t = sin(p)

    p0 = b[0]
    p1 = b[1]
    p2 = b[2]
    p3 = b[3]

    t1 = (1 - t)
    t2 = t1 * t1
    t3 = t2 * t1

    r = p0 * t3 + 3 * p1 * t * t2 + 3 * p2 * t * t * t1 + p3 * (t ** 3)  

    return r


class Heart:

    def __init__(self, generate_frame=20):
        self._points = set()  
        self._edge_diffusion_points = set()  
        self._center_diffusion_points = set()  
        self.all_points = {}  # 
        self.build(2000)  # default, too big may affect calculation

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # 爱心
        for _ in range(number):
            t = random.uniform(0, 2 * pi)  
            x, y = heart_function(t)
            self._points.add((x, y))

        # scatter in
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        # scatter in again
        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.24)  # the bigger then number the more the scatter
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):

        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.47)  

        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * heart_curve(generate_frame / 10 * pi)  

        halo_radius = int(4 + 6 * (1 + heart_halo_curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(heart_halo_curve(generate_frame / 10 * pi) ** 2))

        all_points = []

        # halo
        heart_halo_point = set()  
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi) 
            x, y = heart_function(t, shrink_ratio=heart_halo_curve(generate_frame / 10 * pi) + 11)  
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
        
                heart_halo_point.add((x, y))

                random_int_range = int(27 + heart_halo_curve(generate_frame / 10 * pi) * 4)
                x += random.randint(-random_int_range, random_int_range)
                y += random.randint(-random_int_range, random_int_range)
                size = random.choice((1, 1, 2))
                all_points.append((x, y, size))


        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))


        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)

    def frame_count(self):
        return self.generate_frame


def draw(main: Tk, render_canvas_dict: dict, render_heart: Heart, render_frame=0):
    """
    :param main: TK
    :param render_canvas_dict: cache
    :param render_heart: 
    :param render_frame: 
    :return: None
    """
    frame_index = render_frame % render_heart.frame_count()

    last_frame_index = (frame_index + render_heart.frame_count() - 1) % render_heart.frame_count()
    if last_frame_index in render_canvas_dict:
        render_canvas_dict[last_frame_index].pack_forget()

    if frame_index not in render_canvas_dict:

        canvas = Canvas(
            main,
            bg='black',  
            height=CANVAS_HEIGHT,
            width=CANVAS_WIDTH
        )
        canvas.pack()

        render_heart.render(canvas, render_frame)


        render_canvas_dict[frame_index] = canvas
    else:
        render_canvas_dict[frame_index].pack()

    main.after(
        10,  # the less the better but might lag
        draw, main, render_canvas_dict, render_heart, render_frame + 1)


if __name__ == '__main__':
    print('Creating...')
    start_time = time.time()
    root = Tk()  # 
    root.title(WINDOWS_TITLE)
    canvas_dict = {}
    heart = Heart(40)  # frame
    draw(root, canvas_dict, heart)  
    end_time = time.time()
    print('Heart creation take {:.2f} sec to complete'.format(end_time - start_time))
    root.mainloop()
