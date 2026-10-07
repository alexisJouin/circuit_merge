"""Structures de données partagées ; pas de fenêtre ni de son dans ce module."""

from dataclasses import dataclass
from enum import Enum, auto

import pymunk

from .config import COMPONENTS


class RoundState(Enum):
    """Deux états métier. La pause et les menus appartiennent à l'interface."""

    PLAYING = auto()
    GAME_OVER = auto()


@dataclass
class Piece:
    """Un composant dans le bac.

    ``uid`` identifie UNE instance, ``level`` son type (indice commençant à 0).
    Deux pièces de même niveau ont donc des identifiants différents.
    ``born_at`` et ``overflow_time`` utilisent le temps de simulation.
    """

    uid: int
    level: int
    body: pymunk.Body
    shape: pymunk.Circle
    born_at: float
    overflow_time: float = 0.0

    @property
    def radius(self) -> int:
        """Le rayon reste défini dans le catalogue, sans duplication."""
        return COMPONENTS[self.level].radius


@dataclass(frozen=True)
class GameEvent:
    """Message du moteur vers l'affichage / le son, sans dépendance à Pygame.

    Exemples : ``merge`` crée un anneau et joue une note ; ``impact`` permet
    un bruit discret. L'interface consomme ces événements à chaque image.
    """

    kind: str
    x: float = 0.0
    y: float = 0.0
    level: int = 0
    points: int = 0
    combo: int = 0
