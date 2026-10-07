"""Illustrations électroniques dessinées avec Pygame, sans fichiers d'images.

Chaque illustration est préparée une seule fois, puis mise en cache. Une
rotation transforme le sprite, pas la forme de collision qui reste un disque.
La progression artistique peut être remplacée sans changer les règles.
"""

import pygame

from .config import COMPONENTS

INK = (27, 39, 53)
GOLD = (247, 205, 112)
SILVER = (196, 219, 225)
GREEN = (41, 113, 91)


def draw_component(surface: pygame.Surface, level: int, center: tuple[int, int],
                   size: int) -> None:
    """Dessine l'icône du niveau dans un carré de côté ``size``.

    Les fonctions locales convertissent un repère de conception 100 × 100
    en coordonnées écran : une première illustration du changement d'échelle.
    """
    cx, cy = center
    scale = size / 100

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(cx + (x - 50) * scale), round(cy + (y - 50) * scale)

    def line(color, a, b, width=4):
        pygame.draw.line(surface, color, pt(*a), pt(*b), max(1, round(width * scale)))

    def box(color, x, y, w, h, radius=4, border=0):
        rect = pygame.Rect(*pt(x, y), max(1, round(w * scale)), max(1, round(h * scale)))
        pygame.draw.rect(surface, color, rect, max(0, round(border * scale)),
                         border_radius=max(0, round(radius * scale)))

    def circle(color, x, y, r, border=0):
        pygame.draw.circle(surface, color, pt(x, y), max(1, round(r * scale)),
                           max(0, round(border * scale)))

    if level == 0:  # résistance axiale, bandes colorées et deux pattes
        line(SILVER, (7, 50), (93, 50), 7)
        box((244, 224, 176), 22, 33, 56, 34, 9)
        for x, color in ((32, (93, 53, 37)), (43, (38, 34, 32)),
                         (55, (206, 55, 44)), (68, GOLD)):
            box(color, x, 34, 5, 32, 0)
    elif level == 1:  # LED et méplat
        line(SILVER, (40, 62), (40, 89), 5)
        line(SILVER, (60, 62), (60, 82), 5)
        circle((180, 39, 67), 50, 37, 23)
        box((198, 40, 70), 27, 35, 46, 31, 2)
        box((117, 39, 59), 24, 62, 52, 7, 2)
        line((255, 206, 211), (37, 35), (37, 46), 6)
        line((255, 236, 239), (72, 13), (80, 5), 3)
        line((255, 236, 239), (81, 29), (94, 26), 3)
    elif level == 2:  # condensateur électrolytique
        line(SILVER, (37, 69), (37, 94), 4)
        line(SILVER, (63, 69), (63, 87), 4)
        box((35, 71, 107), 27, 24, 46, 52, 7)
        box((133, 192, 212), 62, 27, 6, 46, 1)
        pygame.draw.ellipse(surface, SILVER, pygame.Rect(*pt(27, 17), round(46 * scale), round(19 * scale)))
        line((109, 137, 157), (37, 21), (63, 32), 2)
        line((109, 137, 157), (37, 32), (63, 21), 2)
        line((224, 244, 250), (37, 52), (46, 52), 2)
        line((224, 244, 250), (41, 47), (41, 57), 2)
    elif level == 3:  # transistor en boîtier TO-92
        for x, y in ((33, 86), (50, 95), (67, 86)):
            line(SILVER, (x, 52), (x, y), 5)
        circle(INK, 50, 36, 29)
        box(INK, 21, 33, 58, 29, 3)
        box((57, 71, 87), 27, 39, 46, 15, 3)
        line((177, 165, 221), (40, 46), (60, 46), 3)
    elif level == 4:  # circuit intégré DIP
        for y in range(25, 80, 11):
            line(GOLD, (11, y), (28, y), 5)
            line(GOLD, (72, y), (89, y), 5)
        box(INK, 26, 14, 48, 72, 7)
        box((52, 68, 83), 33, 27, 34, 48, 3)
        circle((157, 224, 208), 37, 25, 3)
        for y in (41, 51, 61):
            line((154, 184, 185), (40, y), (60, y), 2)
    elif level == 5:  # carte à microcontrôleur
        box(GREEN, 17, 17, 66, 66, 8)
        for x in range(27, 79, 10):
            circle(GOLD, x, 23, 3)
            circle(GOLD, x, 77, 3)
        box(INK, 34, 35, 32, 30, 4)
        box(SILVER, 21, 41, 10, 20, 2)
        circle((84, 244, 164), 73, 35, 4)
        for y in (43, 52, 61):
            line(GOLD, (66, y), (74, y), 2)
        line((120, 195, 159), (44, 34), (44, 25), 2)
    elif level == 6:  # barrette de RAM
        box(GREEN, 6, 29, 88, 39, 4)
        for x in (15, 34, 53, 72):
            box(INK, x, 36, 13, 20, 2)
        for x in range(12, 89, 6):
            box(GOLD, x, 62, 4, 10, 0)
        box(GREEN, 48, 65, 4, 8, 0)
        line((113, 196, 146), (13, 59), (85, 59), 2)
    elif level == 7:  # processeur, substrat et dissipateur métallique
        box(GREEN, 17, 17, 66, 66, 7)
        for pos in range(26, 82, 9):
            line(GOLD, (pos, 10), (pos, 17), 4)
            line(GOLD, (pos, 83), (pos, 90), 4)
            line(GOLD, (10, pos), (17, pos), 4)
            line(GOLD, (83, pos), (90, pos), 4)
        box(SILVER, 26, 26, 48, 48, 5)
        box((226, 237, 238), 30, 30, 40, 36, 4)
        box((56, 106, 137), 38, 39, 24, 20, 3)
        line((154, 207, 231), (43, 49), (57, 49), 2)
    elif level == 8:  # carte graphique à deux ventilateurs
        box(GREEN, 9, 30, 83, 42, 4)
        box(INK, 10, 28, 80, 37, 6)
        for x in (32, 68):
            circle((77, 93, 109), x, 47, 16)
            circle(INK, x, 47, 12)
            for a, b in (((-9, -6), (9, 6)), ((-6, 9), (6, -9))):
                line((154, 173, 186), (x + a[0], 47 + a[1]), (x + b[0], 47 + b[1]), 4)
            circle((199, 161, 229), x, 47, 4)
        for x in range(18, 75, 6):
            box(GOLD, x, 68, 4, 7, 0)
        box(SILVER, 5, 25, 5, 48, 1)
    elif level == 9:  # carte mère, connecteurs et pistes
        box(GREEN, 14, 10, 72, 80, 5)
        for a, b in (((24, 53), (24, 76)), ((24, 76), (69, 76)),
                     ((49, 42), (49, 60)), ((49, 60), (69, 60))):
            line((106, 183, 144), a, b, 2)
        box(SILVER, 28, 26, 29, 29, 3)
        box(INK, 34, 32, 17, 17, 2)
        for x in (66, 75):
            box(INK, x, 22, 5, 40, 1)
        for y in (65, 76):
            box((234, 217, 149), 34, y, 40, 4, 1)
        for y in (22, 40, 58):
            box(SILVER, 9, y, 13, 10, 1)
        for x, y in ((20, 16), (80, 16), (20, 84), (80, 84)):
            circle(GOLD, x, y, 2)
    else:  # supercalculateur : trois baies reliées
        for x in (8, 38, 68):
            box((48, 62, 77), x, 14, 24, 67, 4)
            box(INK, x + 3, 18, 18, 58, 2)
            for y in range(22, 71, 10):
                box((101, 127, 148), x + 5, y, 14, 6, 1)
                circle((92, 240, 167), x + 17, y + 3, 1.5)
        line(GOLD, (20, 85), (80, 85), 3)
        for x in (20, 50, 80):
            line(GOLD, (x, 81), (x, 86), 3)


class SpriteCache:
    """Prépare des disques détaillés et des miniatures de catalogue."""

    def __init__(self) -> None:
        self.cache: dict[tuple[int, int], pygame.Surface] = {}

    def get(self, level: int, radius: int | None = None) -> pygame.Surface:
        """Renvoie le même sprite pour le même niveau et le même rayon."""
        radius = radius or COMPONENTS[level].radius
        key = (level, radius)
        if key in self.cache:
            return self.cache[key]
        # Dessin à résolution double : miniatures et rotations plus douces.
        factor = 2
        r = radius * factor
        side = 2 * r + 12
        surf = pygame.Surface((side, side), pygame.SRCALPHA)
        center = (side // 2, side // 2)
        color = COMPONENTS[level].color
        dark = tuple(int(c * 0.73) for c in color)
        pygame.draw.circle(surf, (*color, 55), center, r + 4)
        pygame.draw.circle(surf, dark, center, r)
        pygame.draw.circle(surf, color, (center[0], center[1] - 2), r - 2)
        pygame.draw.circle(surf, tuple(min(255, c + 26) for c in color), center, r, 2)
        pygame.draw.arc(surf, (255, 255, 255, 145),
                        pygame.Rect(center[0] - r + 6, center[1] - r + 6, 2 * r - 12, 2 * r - 12),
                        0.8, 2.4, max(1, r // 18))
        draw_component(surf, level, center, round(r * 1.56))
        surf = pygame.transform.smoothscale(surf, (side // factor, side // factor))
        self.cache[key] = surf
        return surf
