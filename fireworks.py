import curses
import random
from time import time, sleep
from math import sin, cos, radians, sqrt
import os
import argparse

chars_big = ["#", "%"]
chars_med = ["+", "*"]
chars_small = [".", ",", "'"]


class Particle:
    def __init__(self, xPos: float, yPos: float):
        self.xPos = round(xPos)
        self.yPos = round(yPos)
        self.timestamp = time()

    def draw(self, stdscr, color_pair, max_y, max_x):
        try:
            if (
                self.yPos < 0
                or self.yPos >= max_y
                or self.xPos < 0
                or self.xPos >= max_x
            ):
                return

            if time() - self.timestamp >= decay_time:
                stdscr.addch(self.yPos, self.xPos, " ")
            elif time() - self.timestamp >= decay_time / 1.3:
                char = random.choice(chars_small)
                stdscr.addch(self.yPos, self.xPos, char, curses.color_pair(color_pair))
            elif time() - self.timestamp >= decay_time / 3:
                char = random.choice(chars_med)
                stdscr.addch(self.yPos, self.xPos, char, curses.color_pair(color_pair))
            else:
                char = random.choice(chars_big)
                stdscr.addch(self.yPos, self.xPos, char, curses.color_pair(color_pair))
        except:
            pass


class Trail:
    def __init__(self, color_pair=1):
        self.particles = []
        self.color_pair = color_pair

    def add_particle(self, xPos, yPos, max_y, max_x):
        if yPos < 0 or yPos >= max_y or xPos < 0 or xPos >= max_x:
            return
        self.particles.append(Particle(xPos, yPos))

    def draw(self, stdscr, max_y, max_x):
        for particle in self.particles:
            particle.draw(stdscr, self.color_pair, max_y, max_x)


class Projectile:
    def __init__(self, xPos, yPos, deltaV, acceleration, speed, angle):
        self.xPos = xPos
        self.yPos = yPos
        self.deltaV = deltaV
        self.acceleration = acceleration
        self.xSpeed = sin(radians(-angle)) * speed
        self.ySpeed = cos(radians(-angle)) * speed
        self.angle = angle
        self.color_pair = 1
        self.trail = Trail(self.color_pair)
        self.active = True

    def update_position(self, max_y, max_x):
        self.trail.add_particle(self.xPos, self.yPos, max_y, max_x)

        self.xPos = self.xPos - self.xSpeed
        self.yPos = self.yPos - self.ySpeed
        self.ySpeed -= gravity

        if self.deltaV > 0:
            self.ySpeed += cos(radians(-self.angle)) * self.acceleration
            self.xSpeed += sin(radians(-self.angle)) * self.acceleration

        self.deltaV -= self.acceleration

        if self.yPos < 0 or self.yPos >= max_y or self.xPos < 0 or self.xPos >= max_x:
            self.active = False

    def should_explode(self, max_y):
        return self.yPos < max_y * explosion_height


class Firework(Projectile):
    def __init__(
        self,
        xPos,
        yPos,
        deltaV,
        acceleration,
        speed,
        angle,
        trail_color=1,
        explosion_color=1,
    ):
        super().__init__(xPos, yPos, deltaV, acceleration, speed, angle)
        self.trail_color = trail_color
        self.explosion_color = explosion_color
        self.trail = Trail(self.trail_color)

    def explode(self, projectiles_list, trails_list):
        angle = 0

        fragments = random.randint(fragment_range[0], fragment_range[1])
        for i in range(fragments):
            angle_modifier = random.randint(-10, 10)
            speed = random.uniform(force[0], force[1])
            shrapnel = Projectile(
                self.xPos, self.yPos, 0, 0, speed, angle + angle_modifier
            )
            shrapnel.color_pair = self.explosion_color
            shrapnel.trail = Trail(self.explosion_color)
            projectiles_list.append(shrapnel)
            trails_list.append(shrapnel.trail)
            angle += 360 / fragments


def fireworks_display(stdscr):
    projectiles = []
    trails = []
    stdscr.nodelay(True)

    frame_count = 0
    global gap_between_fireworks
    global ui_toggled
    global speed
    global deltaV

    while True:
        max_y, max_x = stdscr.getmaxyx()

        try:
            key = stdscr.getch()
            if key == ord("q") or key == ord("Q"):
                break
            if key == ord("u") or key == ord("U"):
                if ui_toggled:
                    ui_toggled = False
                else:
                    ui_toggled = True
            if key == ord("]"):
                if gap_between_fireworks > 0.2:
                    gap_between_fireworks -= 0.1
            if key == ord("["):
                gap_between_fireworks += 0.1
            if key == curses.KEY_UP:
                deltaV += 0.5
                speed += 0.2
            if key == curses.KEY_DOWN:
                deltaV = max(0.5, deltaV - 0.5)
                speed = max(0.2, speed - 0.2)
        except:
            pass

        i = 0
        while i < len(projectiles):
            proj = projectiles[i]
            proj.update_position(max_y, max_x)

            if (
                isinstance(proj, Firework)
                and proj.active
                and proj.should_explode(max_y)
            ):
                proj.explode(projectiles, trails)
                projectiles.pop(i)
                continue

            if not proj.active:
                projectiles.pop(i)
                continue

            i += 1

        current_time = time()
        trails[:] = [
            trail
            for trail in trails
            if any(current_time - p.timestamp < decay_time for p in trail.particles)
        ]

        if frame_count % int(gap_between_fireworks * framerate) == 0:
            init_xPos = random.uniform(0.2 * max_x, 0.8 * max_x)
            init_yPos = max_y - 1
            acceleration = random.uniform(0.8, 1)
            angle = random.randint(0, 30)
            if init_xPos > 0.5 * max_x:
                angle = -angle

            firework = Firework(
                init_xPos,
                init_yPos,
                deltaV,
                acceleration,
                speed,
                angle,
                trail_color=0,
                explosion_color=random.randint(1, 6),
            )
            projectiles.append(firework)
            trails.append(firework.trail)

        # Render everything
        try:
            stdscr.erase()
            for trail in trails:
                trail.draw(stdscr, max_y, max_x)
            if ui_toggled:
                stdscr.addstr(1, 1, f"T: {round(gap_between_fireworks, 1)}, deltaV: {round(deltaV, 1)}, Speed: {round(speed,1)}",)
            stdscr.refresh()
        except:
            pass


        frame_count += 1
        sleep(1 / framerate)


def parse_args():
    parser = argparse.ArgumentParser(description="Terminal fireworks display")
    parser.add_argument(
        "--framerate", type=int, default=30, help="Frames per second (default: 30)"
    )
    parser.add_argument(
        "--gravity", type=float, default=0.2, help="Gravity strength (default: 0.2)"
    )
    parser.add_argument(
        "--decay-time",
        type=float,
        default=0.4,
        help="Particle decay time in seconds (default: 0.4)",
    )
    parser.add_argument(
        "--explosion-height",
        type=float,
        default=0.3,
        help="Distance from top of screen where fireworks explode, as a fraction of the screen (default: 0.3)",
    )
    parser.add_argument(
        "--gap",
        type=float,
        default=1.5,
        help="Gap between fireworks in seconds (default: 1.5)",
    )
    parser.add_argument(
        "--fragments",
        type=int,
        nargs=2,
        default=[8, 20],
        help="Min and max explosion fragments (default: 8 20)",
    )
    parser.add_argument(
        "--force",
        type=int,
        nargs=2,
        default=[2.5, 3.5],
        help="Min and max explosion speed (default: 2.5 3.5)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Firework launch speed (default: 1.0)",
    )
    parser.add_argument(
        "--delta-v",
        type=float,
        default=3.0,
        help="Sets how much the rocket can accelerate (default: 3.0)",
    )
    return parser.parse_args()


def main(stdscr):

    if not os.isatty(1) or os.environ.get("TERM") == "dumb":
        print("Error: This script requires a TTY with curses support.")
        return

    global framerate, gravity, decay_time, explosion_height, gap_between_fireworks, fragment_range, speed, deltaV, force, ui_toggled
    args = parse_args()
    framerate = args.framerate
    gravity = args.gravity
    decay_time = args.decay_time
    explosion_height = args.explosion_height
    gap_between_fireworks = args.gap
    fragment_range = args.fragments
    speed = args.speed
    deltaV = args.delta_v
    force = args.force
    ui_toggled = False

    stdscr.clear()
    curses.curs_set(False)
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(0, -1, -1)
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_BLUE, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_CYAN, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)

    try:
        fireworks_display(stdscr)
    except KeyboardInterrupt:
        pass

def main_wrapper():
    curses.wrapper(main)

if __name__ == "__main__":
    main_wrapper()

