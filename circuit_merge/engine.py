"""Règles et physique de Circuit Merge, exécutables sans interface graphique.

Les élèves peuvent tester ce module sans ouvrir de fenêtre. Pymunk calcule
les forces et contacts ; ce fichier décide QUAND deux composants fusionnent.
Voir ``docs/GUIDE_NSI.md`` pour les invariants et le pas de temps fixe.
"""

import math
import random
from typing import Any

import pymunk

from . import config as C
from .model import GameEvent, Piece, RoundState

PIECE_COLLISION, WALL_COLLISION = 1, 2


class GameEngine:
    """Une partie autonome ; le rendu ne doit pas modifier ses corps physiques.

    Une graine optionnelle rend les tirages reproductibles pour les TP.
    Les coordonnées suivent le repère de l'écran : la gravité est positive
    sur y. Le compteur ``time`` avance seulement quand ``step`` est appelée.
    """

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.space = pymunk.Space()
        self.space.gravity = (0, C.GRAVITY)
        self.space.damping = C.AIR_DAMPING
        self.space.iterations = 30
        self.space.collision_slop = 0.35
        self.space.sleep_time_threshold = 0.6
        self.space.idle_speed_threshold = 8.0

        # Deux index pour accéder aux pièces par identifiant ou par forme.
        self.pieces: dict[int, Piece] = {}
        self._by_shape: dict[pymunk.Shape, Piece] = {}
        self._next_uid = 0
        self._merge_queue: set[tuple[int, int]] = set()
        self.events: list[GameEvent] = []
        self.time = 0.0
        self.score = 0
        self.drops = 0
        self.merge_count = 0
        self.highest_level = 0
        self.completed_circuits = 0
        self.combo = 0
        self._last_merge = -math.inf
        self.last_drop = -C.DROP_INTERVAL
        self._last_impact = -math.inf
        self.current_level = self._draw_level()
        self.next_level = self._draw_level()
        self.aim_x = (C.LEFT + C.RIGHT) / 2
        self.state = RoundState.PLAYING
        self._create_walls()

        # pre_solve est rappelée tant que le contact existe. Une fusion
        # différée par MERGE_GRACE sera donc encore détectée au pas suivant.
        self.space.on_collision(PIECE_COLLISION, PIECE_COLLISION,
                                pre_solve=self._on_contact,
                                post_solve=self._on_impact)
        self.space.on_collision(PIECE_COLLISION, WALL_COLLISION,
                                post_solve=self._on_impact)

    def _create_walls(self) -> None:
        """Trois segments statiques forment un bac ouvert en haut."""
        ends = (((C.LEFT, C.WALL_TOP), (C.LEFT, C.FLOOR)),
                ((C.RIGHT, C.WALL_TOP), (C.RIGHT, C.FLOOR)),
                ((C.LEFT, C.FLOOR), (C.RIGHT, C.FLOOR)))
        for a, b in ends:
            wall = pymunk.Segment(self.space.static_body, a, b, C.WALL_THICKNESS)
            wall.friction = C.FRICTION
            wall.elasticity = C.WALL_ELASTICITY
            wall.collision_type = WALL_COLLISION
            self.space.add(wall)

    def _draw_level(self) -> int:
        """Tirage pondéré des petits composants uniquement."""
        return self.rng.choices(range(len(C.DROP_WEIGHTS)), C.DROP_WEIGHTS, k=1)[0]

    def set_aim(self, x: float) -> None:
        """Borne la visée en tenant compte du rayon et de la paroi."""
        margin = C.COMPONENTS[self.current_level].radius + C.WALL_THICKNESS + 1
        self.aim_x = max(C.LEFT + margin, min(C.RIGHT - margin, x))

    @property
    def can_drop(self) -> bool:
        """Lâcher autorisé seulement pendant une partie et hors délai."""
        return (self.state is RoundState.PLAYING
                and self.time - self.last_drop >= C.DROP_INTERVAL - 1e-9)

    def drop(self, x: float | None = None) -> bool:
        """Lâche le composant annoncé, puis fait avancer la file de deux.

        Renvoie False si le lâcher est trop rapide ou la partie terminée.
        Le composant SUIVANT devient toujours le composant COURANT.
        """
        if not self.can_drop:
            return False
        if x is not None:
            self.set_aim(x)
        piece = self.add_piece(self.current_level, (self.aim_x, C.DROP_Y))
        piece.body.velocity = (0, 12)
        self.events.append(GameEvent("drop", self.aim_x, C.DROP_Y, self.current_level))
        self.current_level = self.next_level
        self.next_level = self._draw_level()
        self.set_aim(self.aim_x)  # le nouveau rayon peut être plus grand
        self.last_drop = self.time
        self.drops += 1
        return True

    def add_piece(self, level: int, position: tuple[float, float],
                  velocity: tuple[float, float] = (0.0, 0.0),
                  *, angle: float = 0.0, born_at: float | None = None) -> Piece:
        """Crée un disque rigide : utile aux fusions, sauvegardes et expériences.

        La masse est proportionnelle à l'aire ; Pymunk calcule le moment
        d'inertie. Cette méthode ne compte pas un lâcher et n'ajoute pas de score.
        """
        if not 0 <= level < len(C.COMPONENTS):
            raise ValueError("Niveau de composant invalide")
        radius = C.COMPONENTS[level].radius
        mass = (radius / C.COMPONENTS[0].radius) ** 2
        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        body.position = position
        body.velocity = velocity
        body.angle = angle
        body.velocity_func = self._limit_velocity
        shape = pymunk.Circle(body, radius)
        shape.friction = C.FRICTION
        shape.elasticity = C.ELASTICITY
        shape.collision_type = PIECE_COLLISION
        self._next_uid += 1
        piece = Piece(self._next_uid, level, body, shape,
                      self.time if born_at is None else born_at)
        self.pieces[piece.uid] = piece
        self._by_shape[shape] = piece
        self.space.add(body, shape)
        self.highest_level = max(self.highest_level, level)
        return piece

    @staticmethod
    def _limit_velocity(body: pymunk.Body, gravity: pymunk.Vec2d,
                        damping: float, dt: float) -> None:
        """Intégration standard, puis plafonnement des vitesses extrêmes."""
        pymunk.Body.update_velocity(body, gravity, damping, dt)
        speed = body.velocity.length
        if speed > C.MAX_SPEED:
            body.velocity *= C.MAX_SPEED / speed
        body.angular_velocity = max(-12.0, min(12.0, body.angular_velocity))

    def _on_contact(self, arbiter: pymunk.Arbiter,
                    _space: pymunk.Space, _data: Any) -> None:
        """Signale un candidat à la fusion, sans retirer de corps ici.

        Pymunk verrouille l'espace pendant ``step``. Modifier les collections
        dans ce callback provoquerait une mutation dangereuse de la simulation.
        La file contient des identifiants copiés, jamais des arbitres conservés.
        """
        a, b = (self._by_shape.get(shape) for shape in arbiter.shapes)
        if a is None or b is None or a.level != b.level:
            return
        if min(self.time - a.born_at, self.time - b.born_at) < C.MERGE_GRACE:
            return
        self._merge_queue.add(tuple(sorted((a.uid, b.uid))))

    def _on_impact(self, arbiter: pymunk.Arbiter,
                   _space: pymunk.Space, _data: Any) -> None:
        """Émet peu d'événements : pas de bruit continu sur une pile immobile."""
        if (arbiter.is_first_contact and arbiter.total_ke > 90
                and self.time - self._last_impact > 0.09):
            self.events.append(GameEvent("impact"))
            self._last_impact = self.time

    def _remove_piece(self, piece: Piece) -> None:
        """Maintient les deux index cohérents avec l'espace physique."""
        self.space.remove(piece.shape, piece.body)
        del self.pieces[piece.uid]
        del self._by_shape[piece.shape]

    def _process_merges(self) -> None:
        """Résout chaque paire ; une pièce ne peut être consommée deux fois.

        Tri déterministe : si trois objets identiques se touchent, la première
        paire valide fusionne, puis les autres références deviennent obsolètes.
        Chaque fusion normale diminue de 1 le nombre de pièces présentes.
        """
        pairs = sorted(self._merge_queue)
        self._merge_queue.clear()
        for uid_a, uid_b in pairs:
            a, b = self.pieces.get(uid_a), self.pieces.get(uid_b)
            if a is None or b is None or a.level != b.level:
                continue
            total_mass = a.body.mass + b.body.mass
            position = (a.body.position * a.body.mass + b.body.position * b.body.mass) / total_mass
            velocity = (a.body.velocity * a.body.mass + b.body.velocity * b.body.mass) / total_mass
            angle = (a.body.angle + b.body.angle) / 2
            level = a.level + 1
            self._remove_piece(a)
            self._remove_piece(b)

            if level < len(C.COMPONENTS):
                # Évite une création DANS le sol ou une paroi. Les contacts
                # avec les voisins seront résolus naturellement par Pymunk.
                radius = C.COMPONENTS[level].radius + C.WALL_THICKNESS + 0.5
                x = max(C.LEFT + radius, min(C.RIGHT - radius, position.x))
                y = min(C.FLOOR - radius, position.y)
                self.add_piece(level, (x, y), (velocity.x, velocity.y), angle=angle)
                points = C.COMPONENTS[level].points
            else:
                # Deux objets terminaux disparaissent : la partie reste infinie.
                self.completed_circuits += 1
                points = 2 * C.COMPONENTS[-1].points
                level = len(C.COMPONENTS) - 1

            self.score += points
            self.merge_count += 1
            self.combo = self.combo + 1 if self.time - self._last_merge <= C.COMBO_WINDOW else 1
            self._last_merge = self.time
            self.events.append(GameEvent("merge", position.x, position.y,
                                         level, points, self.combo))
            if level == len(C.COMPONENTS) - 1:
                self.events.append(GameEvent("goal", position.x, position.y, level))

    def step(self, dt: float = C.FIXED_DT) -> None:
        """Avance UN pas fixe ; la boucle graphique gère l'accumulateur.

        Les compteurs sont basés sur dt, jamais sur le nombre d'images rendues.
        Ne pas appeler cette méthode pendant une pause.
        """
        if self.state is not RoundState.PLAYING:
            return
        self.time += dt
        self.space.step(dt)
        self._process_merges()
        self._check_overflow(dt)

    def _check_overflow(self, dt: float) -> None:
        """Défaite si UNE pièce dépasse la limite continuellement trop longtemps.

        Chaque pièce possède son propre chronomètre : deux dépassements brefs
        de pièces différentes ne doivent jamais s'additionner. La grâce évite
        de perdre à cause du composant qui vient juste d'être lâché / fusionné.
        """
        for piece in self.pieces.values():
            above = piece.body.position.y - piece.radius < C.DANGER_Y
            old_enough = self.time - piece.born_at >= C.DROP_GRACE
            piece.overflow_time = piece.overflow_time + dt if above and old_enough else 0.0
            escaped = (piece.body.position.y > C.FLOOR + piece.radius + 100
                       or piece.body.position.x < C.LEFT - piece.radius
                       or piece.body.position.x > C.RIGHT + piece.radius)
            if piece.overflow_time >= C.OVERFLOW_DELAY or (escaped and old_enough):
                self.state = RoundState.GAME_OVER
                self.events.append(GameEvent("game_over"))
                break

    @property
    def danger_ratio(self) -> float:
        """Progression du plus long dépassement, bornée entre 0 et 1."""
        longest = max((p.overflow_time for p in self.pieces.values()), default=0.0)
        return min(1.0, longest / C.OVERFLOW_DELAY)

    @property
    def recent_combo(self) -> int:
        """Nombre de fusions rapprochées, ou zéro si leur affichage a expiré."""
        return self.combo if self.time - self._last_merge < C.COMBO_WINDOW else 0

    def take_events(self) -> list[GameEvent]:
        """Transfère les événements à l'interface et vide la boîte aux lettres."""
        events, self.events = self.events, []
        return events

    def piece_at(self, x: float, y: float) -> Piece | None:
        """Recherche géométrique pour l'inspecteur pédagogique."""
        for piece in reversed(list(self.pieces.values())):
            if (piece.body.position - (x, y)).length <= piece.radius:
                return piece
        return None

    def snapshot(self) -> dict[str, Any]:
        """État JSON : primitives uniquement, pas de sérialisation des corps C.

        Les contacts et les corps endormis sont recalculés au chargement.
        Le résultat est une reprise de partie, pas un rejeu bit à bit.
        """
        return {
            "version": 1, "time": self.time, "score": self.score,
            "drops": self.drops, "merge_count": self.merge_count,
            "highest_level": self.highest_level,
            "completed_circuits": self.completed_circuits,
            "current_level": self.current_level, "next_level": self.next_level,
            "aim_x": self.aim_x, "last_drop": self.last_drop,
            "state": self.state.name, "rng_state": self.rng.getstate(),
            "pieces": [
                {"level": p.level, "position": list(p.body.position),
                 "velocity": list(p.body.velocity), "angle": p.body.angle,
                 "angular_velocity": p.body.angular_velocity,
                 "age": self.time - p.born_at, "overflow_time": p.overflow_time}
                for p in self.pieces.values()
            ],
        }

    @classmethod
    def from_snapshot(cls, data: dict[str, Any]) -> "GameEngine":
        """Reconstruit une partie ; refuse un état incomplet ou non raisonnable."""
        if data.get("version") != 1 or len(data["pieces"]) > 1500:
            raise ValueError("Format de sauvegarde non pris en charge")

        def number(value: Any, low: float, high: float) -> float:
            result = float(value)
            if not math.isfinite(result) or not low <= result <= high:
                raise ValueError("Valeur numérique invalide dans la sauvegarde")
            return result

        def integer(value: Any, low: int, high: int) -> int:
            result = number(value, low, high)
            if not result.is_integer():
                raise ValueError("Entier attendu dans la sauvegarde")
            return int(result)

        engine = cls()
        engine.time = number(data["time"], 0, 1e9)
        for key in ("score", "drops", "merge_count", "completed_circuits"):
            setattr(engine, key, integer(data[key], 0, 10**12))
        engine.highest_level = integer(data["highest_level"], 0, len(C.COMPONENTS) - 1)
        engine.current_level = integer(data["current_level"], 0, len(C.DROP_WEIGHTS) - 1)
        engine.next_level = integer(data["next_level"], 0, len(C.DROP_WEIGHTS) - 1)
        engine.last_drop = number(data["last_drop"], -C.DROP_INTERVAL, engine.time)
        engine.set_aim(number(data["aim_x"], 0, C.WIDTH))
        engine.state = RoundState[data["state"]]

        # JSON transforme les tuples en listes ; Random attend des tuples.
        def tuples(value: Any) -> Any:
            return tuple(tuples(v) for v in value) if isinstance(value, list) else value

        engine.rng.setstate(tuples(data["rng_state"]))
        for item in data["pieces"]:
            level = integer(item["level"], 0, len(C.COMPONENTS) - 1)
            position = tuple(number(v, -500, 2000) for v in item["position"])
            velocity = tuple(number(v, -C.MAX_SPEED, C.MAX_SPEED) for v in item["velocity"])
            if len(position) != 2 or len(velocity) != 2:
                raise ValueError("Vecteur de taille incorrecte")
            piece = engine.add_piece(level, position, velocity,
                                     angle=number(item["angle"], -1e9, 1e9),
                                     born_at=engine.time - number(item["age"], 0, engine.time + 10))
            piece.body.angular_velocity = number(item["angular_velocity"], -12, 12)
            piece.overflow_time = number(item["overflow_time"], 0, C.OVERFLOW_DELAY + 1)
        engine.events.clear()
        return engine
