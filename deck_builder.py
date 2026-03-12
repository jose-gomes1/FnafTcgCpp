"""
FNAF TCG - Deck Builder
Run: python deck_builder.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from engine.cards import ANIMATRONICS, SUPPORTS, AnimatronicCard, SupportCard
from engine.deck import validate_deck, build_deck_from_list, MAX_COPIES_PER_NAME

BANNER = r"""
 ____  _____ ____ _  __   ____  _   _ ___ _     ____  _____ ____  
|  _ \| ____/ ___| |/ /  | __ )| | | |_ _| |   |  _ \| ____|  _ \ 
| | | |  _|| |   | ' /   |  _ \| | | || || |   | | | |  _| | |_) |
| |_| | |__| |___| . \   | |_) | |_| || || |___| |_| | |___|  _ < 
|____/|_____\____|_|\_\  |____/ \___/|___|_____|____/|_____|_| \_\

         Five Nights at Freddy's TCG — Construtor de Deck
"""

DECKS_DIR = os.path.join(os.path.dirname(__file__), "decks")


def ensure_decks_dir():
    os.makedirs(DECKS_DIR, exist_ok=True)


# ── Current deck state ────────────────────────────────────────────────────────

class DeckBuilder:
    def __init__(self):
        self.deck_name = "Novo Deck"
        # spec: list of [qty, name]
        self.spec: list[list] = []

    def total_cards(self) -> int:
        return sum(q for q, _ in self.spec)

    def count_of(self, name: str) -> int:
        return sum(q for q, n in self.spec if n == name)

    def add(self, name: str, qty: int = 1) -> str:
        if name != "Eletricidade":
            if name not in ANIMATRONICS and name not in SUPPORTS:
                return f"Carta desconhecida: '{name}'"
            current = self.count_of(name)
            if isinstance(ANIMATRONICS.get(name), AnimatronicCard):
                if current + qty > MAX_COPIES_PER_NAME:
                    return f"Máximo de {MAX_COPIES_PER_NAME} cópias de '{name}' (já tens {current})."

        for entry in self.spec:
            if entry[1] == name:
                entry[0] += qty
                return f"Adicionado {qty}x {name} (total: {entry[0]})"
        self.spec.append([qty, name])
        return f"Adicionado {qty}x {name}"

    def remove(self, name: str, qty: int = 1) -> str:
        for entry in self.spec:
            if entry[1] == name:
                entry[0] -= qty
                if entry[0] <= 0:
                    self.spec.remove(entry)
                    return f"Removido {name} completamente."
                return f"Removido {qty}x {name} (restam: {entry[0]})"
        return f"'{name}' não está no deck."

    def validate(self) -> tuple[bool, list[str]]:
        try:
            deck = build_deck_from_list([(q, n) for q, n in self.spec])
            return validate_deck(deck)
        except Exception as e:
            return False, [str(e)]

    def show(self):
        print(f"\n{'─'*50}")
        print(f"  DECK: {self.deck_name}  ({self.total_cards()}/30+ cartas)")
        print(f"{'─'*50}")
        if not self.spec:
            print("  (vazio)")
            return

        animatronics = [(q, n) for q, n in self.spec
                        if n in ANIMATRONICS]
        supports = [(q, n) for q, n in self.spec
                    if n in SUPPORTS]
        elec = [(q, n) for q, n in self.spec if n == "Eletricidade"]

        if animatronics:
            print("  ANIMATRONICS:")
            for q, n in animatronics:
                a = ANIMATRONICS[n]
                print(f"    {q}x {n:<30} HP:{a.max_hp}  MaxElec:{a.max_electricity}")
        if supports:
            print("  SUPORTES:")
            for q, n in supports:
                print(f"    {q}x {n}")
        if elec:
            print("  ELETRICIDADE:")
            for q, n in elec:
                print(f"    {q}x ⚡ Eletricidade")

        valid, errors = self.validate()
        print(f"\n  Estado: {'✓ VÁLIDO' if valid else '✗ INVÁLIDO'}")
        for e in errors:
            print(f"    ⚠ {e}")
        print(f"{'─'*50}")

    def save(self) -> str:
        ensure_decks_dir()
        safe_name = self.deck_name.replace(" ", "_").replace("/", "-")
        path = os.path.join(DECKS_DIR, f"{safe_name}.json")
        data = {"name": self.deck_name, "spec": self.spec}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def load(self, path: str):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.deck_name = data["name"]
        self.spec = data["spec"]


# ── Card Browsing ─────────────────────────────────────────────────────────────

def browse_animatronics(filter_str: str = ""):
    cards = list(ANIMATRONICS.values())
    if filter_str:
        cards = [c for c in cards if filter_str.lower() in c.name.lower()]
    if not cards:
        print("Nenhum animatronic encontrado.")
        return
    print(f"\n{'─'*65}")
    print(f"  {'NOME':<30} {'HP':>5} {'MAX⚡':>6}  ATAQUES")
    print(f"{'─'*65}")
    for c in cards:
        atk_str = "  |  ".join(
            f"{a.name}({a.attack_type[0]},{a.cost}⚡,{a.value})"
            for a in c.attacks
        )
        print(f"  {c.name:<30} {c.max_hp:>5} {c.max_electricity:>6}  {atk_str}")
    print(f"{'─'*65}")


def browse_supports(filter_str: str = ""):
    cards = list(SUPPORTS.values())
    if filter_str:
        cards = [c for c in cards if filter_str.lower() in c.name.lower()]
    if not cards:
        print("Nenhum suporte encontrado.")
        return
    print(f"\n{'─'*65}")
    for c in cards:
        print(f"  {c.name:<25} {c.description}")
    print(f"{'─'*65}")


def list_saved_decks() -> list[str]:
    ensure_decks_dir()
    return [f for f in os.listdir(DECKS_DIR) if f.endswith(".json")]


HELP = """
Comandos disponíveis:
  add <nome> [quantidade]    Adicionar carta ao deck (default: 1)
  add elec [quantidade]      Adicionar eletricidades
  remove <nome> [quantidade] Remover carta do deck
  show                       Ver deck atual
  browse anim [filtro]       Ver todos os animatronics
  browse sup [filtro]        Ver todos os suportes
  save                       Guardar deck
  load                       Carregar deck guardado
  rename <nome>              Renomear deck
  new                        Começar deck novo
  validate                   Verificar se o deck é válido
  help                       Mostrar esta ajuda
  exit                       Sair
"""


def main():
    print(BANNER)
    builder = DeckBuilder()
    print("Bem-vindo ao Construtor de Deck! Escreve 'help' para ver os comandos.")

    while True:
        try:
            raw = input(f"\n[{builder.deck_name} | {builder.total_cards()} cartas] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # ── add ──────────────────────────────────────────────────────────────
        if cmd == "add":
            tokens = args.rsplit(maxsplit=1)
            if not tokens:
                print("Uso: add <nome> [quantidade]")
                continue
            try:
                qty = int(tokens[-1])
                name = tokens[0] if len(tokens) > 1 else ""
            except ValueError:
                qty = 1
                name = args
            if not name:
                print("Especifica o nome da carta.")
                continue
            # Normalize "elec" / "eletricidade"
            if name.lower() in ("elec", "eletricidade", "electricity"):
                name = "Eletricidade"
            else:
                # Try case-insensitive match
                match = next((k for k in list(ANIMATRONICS.keys()) + list(SUPPORTS.keys())
                              if k.lower() == name.lower()), None)
                if match:
                    name = match
            print(builder.add(name, qty))

        # ── remove ───────────────────────────────────────────────────────────
        elif cmd == "remove":
            tokens = args.rsplit(maxsplit=1)
            if not tokens:
                print("Uso: remove <nome> [quantidade]")
                continue
            try:
                qty = int(tokens[-1])
                name = tokens[0] if len(tokens) > 1 else ""
            except ValueError:
                qty = 1
                name = args
            if name.lower() in ("elec", "eletricidade"):
                name = "Eletricidade"
            print(builder.remove(name, qty))

        # ── show ─────────────────────────────────────────────────────────────
        elif cmd == "show":
            builder.show()

        # ── browse ───────────────────────────────────────────────────────────
        elif cmd == "browse":
            tokens = args.split(maxsplit=1)
            sub = tokens[0].lower() if tokens else ""
            filt = tokens[1] if len(tokens) > 1 else ""
            if sub in ("anim", "animatronics", "a"):
                browse_animatronics(filt)
            elif sub in ("sup", "suportes", "s", "supports"):
                browse_supports(filt)
            else:
                print("Usa: browse anim [filtro] | browse sup [filtro]")

        # ── save ─────────────────────────────────────────────────────────────
        elif cmd == "save":
            path = builder.save()
            print(f"Deck guardado em: {path}")

        # ── load ─────────────────────────────────────────────────────────────
        elif cmd == "load":
            decks = list_saved_decks()
            if not decks:
                print("Nenhum deck guardado.")
                continue
            print("Decks guardados:")
            for i, d in enumerate(decks):
                print(f"  [{i}] {d}")
            try:
                idx = int(input("Escolhe o número: ").strip())
                path = os.path.join(DECKS_DIR, decks[idx])
                builder.load(path)
                print(f"Deck '{builder.deck_name}' carregado!")
            except (ValueError, IndexError):
                print("Escolha inválida.")

        # ── rename ───────────────────────────────────────────────────────────
        elif cmd == "rename":
            if not args:
                print("Uso: rename <novo nome>")
            else:
                builder.deck_name = args
                print(f"Deck renomeado para '{args}'.")

        # ── new ──────────────────────────────────────────────────────────────
        elif cmd == "new":
            builder = DeckBuilder()
            print("Novo deck criado.")

        # ── validate ─────────────────────────────────────────────────────────
        elif cmd == "validate":
            valid, errors = builder.validate()
            if valid:
                print("✓ Deck válido!")
            else:
                print("✗ Deck inválido:")
                for e in errors:
                    print(f"  • {e}")

        # ── help ─────────────────────────────────────────────────────────────
        elif cmd == "help":
            print(HELP)

        # ── exit ─────────────────────────────────────────────────────────────
        elif cmd in ("exit", "quit", "sair"):
            print("Até logo!")
            break

        else:
            print(f"Comando desconhecido: '{cmd}'. Escreve 'help' para ajuda.")


if __name__ == "__main__":
    main()
