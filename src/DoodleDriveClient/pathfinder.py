from concurrent.futures import thread
from operator import index
import random
from re import T
import threading
import pygame
import sys
import bitarray

# from DoodleDriveClient.ant_colony import AntColony, generate_distance_matrix
import ant_colony

random.seed(10)

# Initialize Pygame
pygame.init()
myfont = pygame.font.SysFont("Comic Sans MS", 15)

# Set up the screen
canvas_width = 500
canvas_height = 800
screen_width = canvas_width + 100
screen_height = canvas_height + 100
screen = pygame.display.set_mode((screen_width, screen_height))
canvas = pygame.Surface((canvas_width, canvas_height))
pygame.display.set_caption("My Pygame Game")


# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Set up game loop variables
clock = pygame.time.Clock()
is_running = True

ROWS = 14
COLUMNS = 10


def generate_preset1():
    preset = []
    for y in range(0, ROWS-1, 2):
        for x in range(COLUMNS):
            if (y//2)%2:
                if x%2:
                    preset.append((COLUMNS-1-x, y))
                    preset.append((COLUMNS-1-x, y+1))
                else:
                    preset.append((COLUMNS-1-x, y+1))
                    preset.append((COLUMNS-1-x, y))
            else:
                if x%2:
                    preset.append((x, y))
                    preset.append((x, y+1))
                else:
                    preset.append((x, y+1))
                    preset.append((x, y))
    if ROWS%2:
        if (ROWS/2)%2:
            for x in range(COLUMNS):
                preset.append((COLUMNS-1-x, ROWS-1))
        else:
            for x in range(COLUMNS):
                preset.append((x, ROWS-1))
    return preset

def generate_preset2():
    preset = []
    # if (ROWS//2)%2:
    for x in range(COLUMNS):
        preset.append((x, 0))
    # else:
    #     for x in range(COLUMNS):
    #         preset2.append((COLUMNS-1-x, 0))

    for y in range(1, ROWS-1, 2):
        for x in range(COLUMNS):
            if not (y//2)%2:
                if x%2:
                    preset.append((COLUMNS-1-x, y))
                    preset.append((COLUMNS-1-x, y+1))
                else:
                    preset.append((COLUMNS-1-x, y+1))
                    preset.append((COLUMNS-1-x, y))
            else:
                if x%2:
                    preset.append((x, y))
                    preset.append((x, y+1))
                else:
                    preset.append((x, y+1))
                    preset.append((x, y))

    if not ROWS%2:
        if (ROWS//2)%2:
            for x in range(COLUMNS):
                preset.append((COLUMNS-1-x, ROWS-1))
        else:
            for x in range(COLUMNS):
                preset.append((x, ROWS-1))
    return preset
presets = [generate_preset1(), generate_preset2()]

# for i in presets:
#     for x in i:
#         print(x)



class point:
    def __init__(self, x, y):
      self.value = 0
      self.set = False
      self.x = x
      self.y = y
    
    def get_screen_pos(self):
        return get_screen_pos(self.x, self.y)

def get_screen_pos(x, y):
    # return (x+1)*(screen_width/(1+COLUMNS)), (y+1)*(screen_height/(1+ROWS))
    return (x)*(canvas_width/(COLUMNS)), (y)*(canvas_height/(ROWS))

def grid_pos(n):
    return n%COLUMNS, n//COLUMNS

def get_grid_pos(screen_x, screen_y):
    # return max(min(round((screen_x/(screen_width/(1+COLUMNS)))-1), COLUMNS-1), 0), max(min(round((screen_y/(screen_height/(1+ROWS)))-1), ROWS-1), 0)
    return max(min(round(((screen_x-50)/(canvas_width/(COLUMNS)))), COLUMNS-1), 0), max(min(round(((screen_y-50)/(canvas_height/(ROWS)))), ROWS-1), 0)

def get_array_pos(x, y):
    return (COLUMNS*y) + x

def get_preset_pos(x, y, preset):
    for num, i in enumerate(preset):
        if i == (x, y):
            return num 

grid = [
   point(i%COLUMNS, i//COLUMNS) for i in range(ROWS*COLUMNS)
]

# for i in grid:
#     print(i.x, i.y)
string = "Elia Vandini"
ba = bitarray.bitarray()
ba.frombytes(string.encode('utf-8'))
word_mask = ba.tolist()
# word_mask = [1 for _ in range(0, 1000)]
# print(word_mask)

preset = []
selected = [grid_pos(0), grid_pos((COLUMNS*ROWS)-1)]
# selected = []
# stm_points = [[0,1], [0,0], [1,0], [1,1], [2,1], [2,0], [3,0], [3,1], [4,1], [4,0], [5,0], [5,1], [6,1], [6,0], [7,0], [7,1], [8,1], [8,0], [9,0], [9,1], [9,3], [9,2], [8,2], [8,3], [7,3], [7,2], [6,2], [6,3], [5,3], [5,2], [4,2], [4,3], [3,3], [3,2], [2,2], [2,3], [1,3], [1,2], [0,2], [0,3], [0,5], [0,4], [1,4], [1,5], [2,5], [2,4], [3,4], [3,5], [4,5], [4,4], [5,4], [5,5], [6,5], [6,4], [7,4], [7,5], [8,5], [8,4], [9,4], [9,5], [9,7], [9,6], [8,6], [8,7], [7,7], [7,6], [6,6], [6,7], [5,7], [5,6], [4,6], [4,7], [3,7], [3,6], [2,6], [2,7], [1,7], [1,6], [0,6], [0,7], [0,9], [0,8], [1,8], [1,9], [2,9], [2,8], [3,8], [3,9], [4,9], [4,8], [5,8], [5,9], [6,9], [6,8], [7,8], [7,9], [8,9], [8,8], [9,8], [9,9], [9,11], [9,10], [8,10], [8,11], [7,11], [7,10], [6,10], [6,11], [5,11], [5,10], [4,10], [4,11], [3,11], [3,10], [2,10], [2,11], [1,11], [1,10], [0,10], [0,11], [0,13], [0,12], [1,12], [1,13], [2,13], [2,12], [3,12], [3,13], [4,13], [4,12], [5,12], [5,13], [6,13], [6,12], [7,12], [7,13], [8,13], [8,12], [9,12], [9,13], ]
# stm_points = [(1, 0), (2, 0), (2, 2), (3, 2), (3, 3), (4, 3), (5, 2), (6, 2), (7, 3), (6, 4), (5, 4), (5, 5), (4, 5), (3, 5), (2, 4), (1, 4), (0, 5), (0, 6), (1, 7), (1, 8), (2, 8), (2, 9), (3, 9), (3, 10), (3, 11), (3, 12), (2, 12), (1, 12), (1, 13), (0, 13), (0, 11), (0, 10), (0, 9), (1, 10), (4, 8), (4, 7), (3, 7), (5, 6), (6, 6), (6, 7), (6, 8), (7, 8), (7, 9), (8, 9), (8, 10), (8, 11), (7, 11), (6, 11), (6, 10), (5, 10), (4, 11), (5, 13), (9, 12), (9, 11), (9, 10), (9, 8), (8, 7), (8, 6), (8, 5), (7, 5), (9, 4), (9, 3), (9, 2), (8, 1), (9, 0), (7, 0), (7, 1), (4, 1), (0, 1), (1, 0)]

# Example usage:
num_points = 10
min_coord = 0
max_coord = 100
random.seed(10)
random_points = []
# print(get_array_pos(*selected[0]), get_array_pos(*selected[1]))
for i in range(get_array_pos(*selected[0]), get_array_pos(*selected[1])+1):
    grid[i].set = True
    # random.seed(1)
    # if random.randint(0, 1):
    def safe_list_get (l, idx, default):
        try:
            return l[idx]
        except IndexError:
            return default
    if safe_list_get(word_mask, i-get_array_pos(*selected[0]), 0):
        random_points.append((grid[i].x, grid[i].y))
        grid[get_array_pos(grid[i].x, grid[i].y)].value = 1
# random_points = generate_random_points(num_points, min_coord, max_coord)
# random_points = [(1, 0), (2, 0), (7, 0), (1, 1), (2, 1), (6, 1), (1, 2), (2, 2), (6, 2), (7, 2), (1, 3), (2, 3), (5, 3), (1, 4), (2, 4), (5, 4), (7, 4), (1, 5), (2, 5), (5, 5), (6, 5), (1, 6), (2, 6), (5, 6), (6, 6), (7, 6), (1, 7), (2, 7), (4, 7), (1, 8), (2, 8), (4, 8), (7, 8), (1, 9), (2, 9), (4, 9), (6, 9), (1, 10), (2, 10), (4, 10), (6, 10), (7, 10), (1, 11), (2, 11), (4, 11), (5, 11), (1, 12), (2, 12), (4, 12), (5, 12), (7, 12), (1, 13), (2, 13), (4, 13), (5, 13), (6, 13)]
# random_points = [(i%COLUMNS, i//COLUMNS) for i in range(111)]

setpoint = [(1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (3, 3), (4, 3), (5, 3), (5, 2), (5, 1), (5, 0), (4, 0), (0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (3, 5), (5, 5), (6, 4), (7, 3), (6, 2), (7, 1), (8, 1), (9, 0), (9, 3), (9, 4), (9, 5), (8, 5), (7, 5), (7, 6), (6, 6), (5, 6), (7, 7), (8, 7), (9, 8), (8, 9), (7, 9), (6, 10), (5, 10), (5, 9), (5, 8), (4, 8), (4, 7), (3, 7), (3, 6), (2, 6), (1, 6), (0, 7), (1, 8), (2, 8), (2, 9), (2, 10), (3, 10), (3, 11), (4, 11), (4, 12), (5, 12), (5, 13), (7, 13), (8, 13), (9, 12), (8, 11), (2, 13), (0, 13), (1, 12), (2, 12), (1, 11), (0, 10), (0, 9), (0, 5)]

# def is_intersection(p1, p2, p3, p4):
#     """Check if line segment (p1,p2) intersects (p3,p4)."""
#     def ccw(A, B, C):
#         return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

#     return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

# def untagle(points):
#     intersecting_segments = []
#     untangle = points.copy()

#     # Check for intersections between line segments
#     while True:
#         intersecting_segments = []
#         for i in range(len(untangle) - 2):
#             for j in range(i + 2, len(untangle) - 1):
#                 if is_intersection(untangle[i], untangle[i+1], untangle[j], untangle[j+1]):
#                     intersecting_segments.append((i, i+1, j, j+1))
#         print(intersecting_segments)
#         if len(intersecting_segments):
#             i1, i2, j1, j2 = intersecting_segments[0]
#             untangle[i2:j1+1] = untangle[i2:j1+1][::-1]
#         else:
#             break
#     return untangle


# intersecting_segments = []

#     # Check for intersections between line segments
#     for i in range(len(points) - 2):
#         for j in range(i + 2, len(points) - 1):
#             if is_intersection(points[i], points[i+1], points[j], points[j+1]):
#                 intersecting_segments.append((i, i+1, j, j+1))

#     # Break segments at intersection points and reconnect
#     for intersection in intersecting_segments:
#         i1, i2, j1, j2 = intersection
#         points[i2:j1+1] = points[i2:j1+1][::-1]

#     return points

# untangled = untagle(setpoint)
# untangled = setpoint

# print(random_points)
# print(distances)

n_ants = 50
n_iterations = 35
decay_rate = 0.005
alpha = 1
beta = 2
rho = 0.1

aco = ant_colony.AntColony(random_points, n_ants, n_iterations, decay_rate, alpha, beta, rho)
t = threading.Thread(target=aco.run)
t.start()

# print("Global Best Path:", [random_points[i] for i in aco.global_best_path])
# stm_points = [random_points[i] for i in aco.global_best_path]
# stm_points = []







preset_index = 0
hoovered = None

while is_running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame.MOUSEBUTTONUP:
            # if event.key == pygame.BUTTON1:
            selected.append(get_grid_pos(*pygame.mouse.get_pos()))
            # print(*selected)
            # print(get_array_pos(*selected[0]),", ", get_array_pos(*selected[1]))
                # if not selected[0][1]%2:
                #     preset = preset1
                #     if COLUMNS - selected[0][0] < selected[1][0] and not selected[0][1] - selected[0][1] %2:
                #         preset = preset2
                # else:
                #     preset = preset2
                #     if COLUMNS - selected[0][0] < selected[1][0] and not selected[0][1] - selected[0][1] %2:
                #         preset = preset1
    hoovered = get_grid_pos(*pygame.mouse.get_pos())

    
    screen.fill(BLACK)
    canvas.fill(BLACK)
    try:
        pygame.draw.lines(canvas, (0, 0, 255), False, [get_screen_pos(*i) for i in [random_points[x] for x in aco.global_best_path]], width=9)
    except Exception as e:
        pass
    # try:
    #     pygame.draw.lines(canvas, (0, 0, 255), False, [get_screen_pos(*i) for i in setpoint], width=9)
    # except Exception as e:
    #     pass
    # try:
    #     pygame.draw.lines(canvas, (0, 255, 255), False, [get_screen_pos(*i) for i in untangled], width=3)
    # except Exception as e:
    #     pass
    # try:
    #     pygame.draw.lines(canvas, (0, 255, 0), False, [get_screen_pos(*i) for i in untangled], width=3)
    # except Exception as e:
    #     pass
        
    if len(selected) == 2:
        selected.sort(key=lambda x: get_array_pos(*x))
        to_path = []
        # print(get_array_pos(*selected[0]), get_array_pos(*selected[1]))
        for i in range(get_array_pos(*selected[0]), get_array_pos(*selected[1])+1):
            grid[i].set = True
            # random.seed(1)
            # if random.randint(0, 1):
            def safe_list_get (l, idx, default):
                try:
                    return l[idx]
                except IndexError:
                    return default
            if safe_list_get(word_mask, i-get_array_pos(*selected[0]), 0):
                to_path.append((grid[i].x, grid[i].y))
                grid[get_array_pos(grid[i].x, grid[i].y)].value = 1
            
        path = []
        p = []
        # print("to path: ", to_path)
        curr_distance = 9999999
        for n, preset in enumerate(presets):
            p = []
            filtered_preset = [get_preset_pos(*i, preset) for i in to_path]
            filtered_preset.sort()
            for i in filtered_preset:
                if preset[i] in to_path and preset[i]:
                    p.append(preset[i])
            straight_distance = 0
            for i in range(1, len(p)):
                if p[i][1] == p[i-1][1]:
                # if abs(p[i][0] - p[i-1][0]) == 1 and p[i][1] == p[i-1][1]:
                    straight_distance = straight_distance +1
            if straight_distance < curr_distance:
                curr_distance = straight_distance
                path = p
                preset_index = n
            # print(straight_distance, len(p), len(filtered_preset), n)
        
        # print(len(path), preset_index, curr_distance)
        preset = presets[preset_index]
                
                
        # print(path)
        # print(path)
        # if len(path) >= 2:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        #     pygame.draw.lines(canvas, (0, 255, 0), False, [get_screen_pos(i[0], i[1]) for i in path], width=3)

    if len(selected) == 3:
        selected = [selected[-1]]
        for i in grid:
            i.set = False
            i.value = 0

    
    # Draw
    for i in grid:
        pygame.draw.circle(canvas, WHITE if i.value else GRAY, i.get_screen_pos(), 2+(i.set*4), width=0)
    if hoovered is not None:
        pygame.draw.circle(canvas, WHITE if i.value else GRAY, get_screen_pos(*hoovered), 10, width=0)
        # Draw here
    # for i in preset1:
    # [i.value for i in grid]
    # if len(presets[preset_index]) > 2:
        # pygame.draw.lines(canvas, (255, 0, 0), False, [get_screen_pos(i[0], i[1]) for i in presets[preset_index]], width=1)
        
        
    
    # Update display
    screen.blit(canvas, (50, 50))
    label = myfont.render(f"{get_grid_pos(*pygame.mouse.get_pos())}", 1, WHITE)
    screen.blit(label, (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] - 10 ))
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
# thread.
aco.stop = True
pygame.quit()
sys.exit()