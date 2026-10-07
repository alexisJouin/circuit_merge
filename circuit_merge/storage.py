"""Sauvegarde locale JSON et écriture atomique.

Une erreur de disque ne doit pas interrompre la partie. On garde un message
lisible pour l'interface et n'écrase pas silencieusement un fichier corrompu.
"""

import json
import os
from pathlib import Path
from typing import Any


def default_save_path() -> Path:
    """Dossier utilisateur, même si le programme est installé en lecture seule."""
    root = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    return root / "CircuitMerge" / "save.json"


class SaveStore:
    """Conserve le record, les options et la partie interrompue."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_save_path()
        self.error = ""

    def load(self) -> dict[str, Any]:
        """Renvoie des valeurs par défaut si le fichier n'existe pas."""
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("version") != 1:
                raise ValueError("Format de sauvegarde inconnu")
            best = data.get("best", 0)
            if not isinstance(best, int) or not 0 <= best <= 10**12:
                raise ValueError("Record invalide")
            return data
        except FileNotFoundError:
            return {"version": 1, "best": 0, "sound": True, "round": None}
        except (OSError, ValueError, TypeError, RecursionError):
            self.error = "Sauvegarde illisible : nouveau départ (original conservé)."
            # Un nom unique évite d'écraser une précédente sauvegarde endommagée.
            import time
            backup = self.path.with_name(f"save_corrompue_{time.time_ns()}.json")
            try:
                self.path.rename(backup)
            except OSError:
                pass
            return {"version": 1, "best": 0, "sound": True, "round": None}

    def save(self, best: int, sound: bool, round_data: dict[str, Any] | None) -> bool:
        """Remplace le fichier seulement après une écriture complète.

        ``os.replace`` est atomique sur un même système de fichiers. Une coupure
        pendant l'écriture laisse donc généralement la sauvegarde précédente.
        """
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.path.with_suffix(".tmp")
            content = {"version": 1, "best": best, "sound": sound, "round": round_data}
            with temp.open("w", encoding="utf-8") as stream:
                json.dump(content, stream, ensure_ascii=False, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, self.path)
            self.error = ""
            return True
        except (OSError, ValueError, TypeError):
            self.error = "Sauvegarde impossible ; la partie continue."
            return False
