from pico2d import *

import random
import math
import game_framework
import game_world
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
import archery_mode

PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0


class Archery_ai:

    def __init__(self):
        self.font = load_font('ENCR10B.TTF', 20)
        self.x = 400
        self.y = 55
        self.frame = 0
        self.action = 0
        self.dir = 1
        self.state = 'Idle'
        self.tx, self.ty = 1000, 1000
        self.build_behavior_tree()
        self.image_Idle = load_image('resource/Archery/ai_idle.png')
        self.image_Run = load_image('resource/Archery/ai_run.png')
        self.patrol_locations = [(43, 274), (1118, 274), (1050, 494), (575, 804), (235, 991), (575, 804), (1050, 494),
                                 (1118, 274)]
        self.loc_no = 0

    def get_bb(self):
        return self.x - 40, self.y - 35, self.x + 50, self.y + 40

    def update(self):
        # self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        # fill here
        self.frame = (self.frame + 0.1) % 7
        self.bt.run()

    def draw(self):
        if self.state == 'Idle':
            self.image_Idle.clip_draw(0, 0, 38, 54, self.x , self.y, 60, 80)
        if self.state == 'Run' and self.dir <= 0:
            self.image_Run.clip_draw(int(self.frame) * 56 + 8, 66, 56, 54, self.x , self.y, 80, 80)

            pass
        elif self.state == 'Run' and self.dir > 0:
            self.image_Run.clip_draw(int(self.frame) * 56 + 8, 0, 56, 54, self.x , self.y, 80, 80)

            pass

        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'zombie:ball':
            self.ball_count += 1

    def set_target_location(self, x=None, y=None):
        if not x or not y:
            raise ValueError('위치 지정을 해야 합니다.')
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS

    def distance_less_than(self, x1, y1, x2, y2, r):
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 < (r * PIXEL_PER_METER) ** 2

    def move_slightly_to(self, tx, ty):
        self.dir = math.atan2(ty - self.y, tx - self.x)
        self.speed = RUN_SPEED_PPS
        self.x += self.speed * math.cos(self.dir) * game_framework.frame_time
        self.y += self.speed * math.sin(self.dir) * game_framework.frame_time

    def move_to(self, r=0.5):  # 0.5 미터
        self.state = 'Run'
        self.move_slightly_to(self.tx, self.ty)
        if self.distance_less_than(self.tx, self.ty, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING

    def set_random_location(self):
        self.tx, self.ty = random.randint(100, 1280 - 100), random.randint(100, 1024 - 100)
        return BehaviorTree.SUCCESS

    def is_boy_nearby(self, r):
        if self.distance_less_than(play_mode.boy.x, play_mode.boy.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def move_to_boy(self, r=0.5):
        self.state = 'Run'
        self.move_slightly_to(play_mode.boy.x, play_mode.boy.y)
        if self.distance_less_than(play_mode.boy.x, play_mode.boy.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING

    def get_patrol_location(self):
        self.tx, self.ty = self.patrol_locations[self.loc_no]
        self.loc_no = (self.loc_no + 1) % len(self.patrol_locations)
        return BehaviorTree.SUCCESS

    def build_behavior_tree(self):
        a1 = Action('Set target location', self.set_target_location, 500, 50)
        a2 = Action('Move to', self.move_to)

        SEQ_move_to_target_location = Sequence('Move to target location', a1, a2)

        a3 = Action('Set random location', self.set_random_location)

        SEQ_wander = Sequence('Wander', a3, a2)

        c1 = Condition('소년이 근처에 있는가?', self.is_boy_nearby, 7)  # 7미터
        a4 = Action('소년한테 접근', self.move_to_boy)

        SEQ_chase_boy = Sequence('소년을 추적', c1, a4)

        SEL_chase_or_wander = Selector('추적 또는 배회', SEQ_chase_boy, SEQ_wander)

        a5 = Action('순찰 위치 가져오기', self.get_patrol_location)
        root = SEQ_patrol = Sequence('순찰', a5, a2)

        self.bt = BehaviorTree(root)
