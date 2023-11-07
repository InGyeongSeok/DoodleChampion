from pico2d import *


import game_framework
import game_world
import title_mode

from archery_background import Archery_background
from archery_target import Target_50, Target_100
from archery_hero import Archery_cat
# Game object class here


def handle_events():

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            archery_cat.handle_event(event)

def init():
    global archery_cat
    global archery_score

    archery_score = 0
    archery_background = Archery_background()
    game_world.add_object(archery_background, 0)

    archery_cat = Archery_cat()
    game_world.add_object(archery_cat, 0)

    target_50 = [Target_50() for i in range(5)]
    game_world.add_objects(target_50, 0)

    target_100 = [Target_100() for i in range(3)]
    game_world.add_objects(target_100, 0)

    # target_50 = Target_50()
    # game_world.add_object(target_50)

    # target_100 = Target_100()
    # game_world.add_object(target_100)

    for s_score in target_50:
        game_world.add_collision_pair('s_score:arrow', s_score, None)

    for b_score in target_100:
        game_world.add_collision_pair('b_score:arrow', b_score, None)

def update():
    game_world.update()
    game_world.handle_collision()




def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()
    pass

def pause():
    archery_cat.wait_time = 100000000000000000000000000000000000.0
    pass

def resume():
    archery_cat.wait_time = get_time()
    pass
