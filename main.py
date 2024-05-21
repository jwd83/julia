# hotkeys:
#
# s - search mode (default)
# z - zoom mode
# i - double the iteration limit
# j - halve the iteration limit
# r - reset the ranges and iteration limit


import pygame
from numba import njit
import numpy as np
from enum import Enum, auto


class Modes(Enum):
    search = auto()
    zoom = auto()


mode = Modes.search

# Adapted from the following code:
# https://github.com/Apsis/Synthetic-Programming


@njit
def generate_julia(
    width,
    height,
    imaginary,
    real,
    re_min,
    re_max,
    im_min,
    im_max,
    iteration_limit,
):

    c = complex(real, imaginary)
    real_range = np.arange(re_min, re_max, (re_max - re_min) / width)
    image_range = np.arange(im_max, im_min, (im_min - im_max) / height)
    julia_set = np.zeros((width, height))
    for i, im in enumerate(image_range):
        for j, re in enumerate(real_range):
            z = complex(re, im)
            n = iteration_limit
            while abs(z) < 10 and n > 0:
                z = z * z + c
                n -= 1
            julia_set[j, i] = n

    return julia_set


pygame.init()

clock = pygame.time.Clock()

display_info = pygame.display.Info()
w = display_info.current_w
h = display_info.current_h

print(f"Screen width: {w}, height: {h}")

# set the screen size
screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)

# get the initial mouse position to real and imaginary parts
iteration_limit = 32

re_min = -2.0
re_max = 2.0
im_min = -2.0
im_max = 2.0

x, y = pygame.mouse.get_pos()
real = re_min + (re_max - re_min) * x / w
imaginary = im_max + (im_min - im_max) * y / h

z_real = re_min + (re_max - re_min) * x / w
z_imaginary = im_max + (im_min - im_max) * y / h

zoom_start = None

running = True
while running:
    # convert the mouse position to real and imaginary parts
    x, y = pygame.mouse.get_pos()

    if mode == Modes.search:

        real = re_min + (re_max - re_min) * x / w
        imaginary = im_max + (im_min - im_max) * y / h
    elif mode == Modes.zoom:

        z_real = re_min + (re_max - re_min) * x / w
        z_imaginary = im_max + (im_min - im_max) * y / h

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                iteration_limit *= 2
            elif event.key == pygame.K_j:
                iteration_limit = max(1, iteration_limit // 2)
            elif event.key == pygame.K_ESCAPE:
                running = False
                zoom_start = None
            elif event.key == pygame.K_s:
                mode = Modes.search
                zoom_start = None
            elif event.key == pygame.K_z:
                mode = Modes.zoom
                zoom_start = None
            elif event.key == pygame.K_r:
                re_min = -2.0
                re_max = 2.0
                im_min = -2.0
                im_max = 2.0
                zoom_start = None
                iteration_limit = 32
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if mode == Modes.zoom:

                    if zoom_start is not None:
                        if zoom_start[0] == z_real or zoom_start[1] == z_imaginary:
                            zoom_start = None
                        else:
                            re_min = min(zoom_start[0], z_real)
                            re_max = max(zoom_start[0], z_real)
                            im_min = min(zoom_start[1], z_imaginary)
                            im_max = max(zoom_start[1], z_imaginary)

                            # fix the aspect ratio to be the same as the screen
                            if (re_max - re_min) / (im_max - im_min) > w / h:
                                im_max = im_min + (re_max - re_min) * h / w

                            zoom_start = None
                    else:
                        zx = x
                        zy = y
                        zoom_start = (z_real, z_imaginary)

    julia_set = generate_julia(
        w, h, imaginary, real, re_min, re_max, im_min, im_max, iteration_limit
    )

    # create a surface from the julia set
    surface = pygame.surfarray.make_surface(julia_set)
    screen.blit(surface, (0, 0))

    font = pygame.font.Font(None, 36)

    # draw the real and imaginary parts of the current position
    text = font.render("mode: " + str(mode), True, (255, 255, 255))
    screen.blit(text, (10, 10))
    text = font.render(
        f"seed: real, imaginary: {real:.5f}, {imaginary:.5f}", True, (255, 255, 255)
    )
    screen.blit(text, (10, 40))

    # draw the ranges
    text = font.render(
        f"real range: {re_min:.5f} - {re_max:.5f}", True, (255, 255, 255)
    )
    screen.blit(text, (10, 70))
    text = font.render(
        f"imaginary range: {im_min:.5f} - {im_max:.5f}", True, (255, 255, 255)
    )
    screen.blit(text, (10, 100))

    # draw the iteration limit
    text = font.render(f"iteration limit: {iteration_limit}", True, (255, 255, 255))
    screen.blit(text, (10, 130))

    if mode == Modes.zoom:
        text = font.render(
            f"zoom real: {z_real}, imaginary: {z_imaginary}", True, (255, 255, 255)
        )
        screen.blit(text, (10, 160))

        if zoom_start is not None:
            text = font.render(
                f"zoom start real: {zoom_start[0]}, imaginary: {zoom_start[1]}",
                True,
                (255, 255, 255),
            )
            screen.blit(text, (10, 190))

            # draw a rectangle from zx, zy to x, y
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (zx, zy, x - zx, y - zy),
                2,
            )

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
quit()
