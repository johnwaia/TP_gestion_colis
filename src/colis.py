from dataclasses import dataclass

PRIORITE_MIN = 1
PRIORITE_MAX = 5


@dataclass(slots=True)
class Colis:
    id: int
    poids: int
    valeur: float
    priorite: int
    destination: str

    def __post_init__(self):
        if not isinstance(self.poids, int) or self.poids <= 0:
            raise ValueError("Le poids doit être un entier strictement positif.")
        if self.valeur < 0:
            raise ValueError("La valeur doit être positive.")
        if not PRIORITE_MIN <= self.priorite <= PRIORITE_MAX:
            raise ValueError(f"La priorité doit être comprise entre {PRIORITE_MIN} et {PRIORITE_MAX}.")
        if not self.destination.strip():
            raise ValueError("La destination ne peut pas être vide.")

    def __str__(self):
        return (f"{self.id:>7} | {self.poids:>6} kg | {self.valeur:>9.2f} € | "
                f"P{self.priorite} | {self.destination}")


ENTETE = "     ID |  Poids     |    Valeur   | Pr | Destination"
