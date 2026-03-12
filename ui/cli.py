"""
FNAF TCG - CLI User Interface
"""
from engine.cards import AnimatronicCard, SupportCard, ElectricityCard


# ── Generic Helpers ───────────────────────────────────────────────────────────

def pick_index(prompt: str, items: list) -> int:
    """Show numbered list, ask user to pick one. Returns index."""
    for i, item in enumerate(items):
        print(f"  [{i}] {item}")
    while True:
        try:
            val = int(input(f"{prompt} (número): "))
            if 0 <= val < len(items):
                return val
        except (ValueError, KeyboardInterrupt):
            pass
        print(f"  Por favor escolhe um número entre 0 e {len(items)-1}.")


def pick_multi_index(prompt: str, items: list, min_n: int = 1, max_n: int = 1) -> list[int]:
    """Pick multiple indices."""
    for i, item in enumerate(items):
        print(f"  [{i}] {item}")
    while True:
        try:
            raw = input(f"{prompt} (números separados por espaço, {min_n}-{max_n}): ")
            vals = [int(x) for x in raw.split()]
            if min_n <= len(vals) <= max_n and all(0 <= v < len(items) for v in vals):
                return vals
        except (ValueError, KeyboardInterrupt):
            pass
        print("  Seleção inválida.")


def yes_no(prompt: str) -> bool:
    while True:
        r = input(f"{prompt} (s/n): ").strip().lower()
        if r in ("s", "sim", "y", "yes"):
            return True
        if r in ("n", "nao", "não", "no"):
            return False


def pick_animatronic_from_deck(player) -> AnimatronicCard | None:
    """Search deck for an animatronic, place it in hand/active."""
    animatronics = [c for c in player.deck if isinstance(c, AnimatronicCard)]
    if not animatronics:
        print("  Nenhum animatronic no deck.")
        return None
    idx = pick_index("Escolhe um animatronic do deck:", animatronics)
    chosen = animatronics[idx]
    player.deck.remove(chosen)
    from engine.player import MAX_ACTIVE
    if len(player.active) < MAX_ACTIVE:
        player.active.append(chosen)
    else:
        player.hand.append(chosen)
    import random
    random.shuffle(player.deck)
    return chosen


# ── Display ───────────────────────────────────────────────────────────────────

def display_game_state(game):
    from engine.game import Game
    p = game.current_player()
    opp = game.opponent()
    print("\n" + "░" * 60)
    print(f"  OPONENTE: {opp.name}  |  Pontos: {opp.points}  |  Deck: {len(opp.deck)}")
    print("  Ativos do oponente:")
    for i, a in enumerate(opp.active):
        stall = f" [STALL {a.stalled_turns}t]" if a.stalled_turns > 0 else ""
        print(f"    [{i}] {a.name}  HP:{a.current_hp}/{a.max_hp}  ⚡{a.electricity}{stall}")
    print("░" * 60)
    print(f"  {p.name}  |  Pontos: {p.points}  |  Deck: {len(p.deck)}")
    print("  Sua party:")
    for i, a in enumerate(p.active):
        stall = f" [STALL {a.stalled_turns}t]" if a.stalled_turns > 0 else ""
        print(f"    [{i}] {a.name}  HP:{a.current_hp}/{a.max_hp}  ⚡{a.electricity}/{a.max_electricity}{stall}")
    print(f"  Mão ({len(p.hand)} cartas):")
    for i, c in enumerate(p.hand):
        print(f"    [{i}] {c}")
    elec_attached = "✓" if p.has_attached_electricity else "✗"
    print(f"  Eletricidade attachada este turno: {elec_attached}")
    print("░" * 60)


# ── Main Turn Loop ────────────────────────────────────────────────────────────

ACTIONS = """
Ações disponíveis:
  [1] Attchar eletricidade a um animatronic
  [2] Colocar animatronic da mão
  [3] Atacar com um animatronic
  [4] Usar suporte
  [5] Ver detalhes de um animatronic
  [0] Terminar turno
"""


def run_player_turn(game):
    """Interactive turn for the current (human) player."""
    p = game.current_player()
    opp = game.opponent()
    attacked_indices = set()  # indices in p.active that already attacked this turn

    while not game.game_over:
        display_game_state(game)
        print(ACTIONS)
        choice = input("Escolha: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            # Attach electricity
            if not p.active:
                print("Nenhum animatronic ativo.")
                continue
            if p.has_attached_electricity:
                print("Já attachaste eletricidade este turno.")
                continue
            if p.electricity_in_hand() == 0:
                print("Sem eletricidades na mão.")
                continue
            idx = pick_index("Attchar em qual animatronic?", p.active)
            game.do_attach_electricity(idx)

        elif choice == "2":
            anim = p.animatronics_in_hand()
            if not anim:
                print("Sem animatronics na mão.")
                continue
            if len(p.active) >= 4:
                print("Party cheia (máximo 4).")
                continue
            idx = pick_index("Colocar qual animatronic?", anim)
            game.do_place_animatronic(idx)

        elif choice == "3":
            alive = [
                (i, a) for i, a in enumerate(p.active)
                if a.can_attack() and i not in attacked_indices
            ]
            if not alive:
                print("Nenhum animatronic disponível para atacar.")
                continue
            if game.round == 1 and game.turn == game.first_player:
                print("O primeiro jogador não pode atacar no primeiro turno!")
                continue

            display_list = [a for _, a in alive]
            pick = pick_index("Atacar com qual animatronic?", display_list)
            a_idx, attacker = alive[pick]

            if not attacker.attacks:
                print("Sem ataques disponíveis.")
                continue
            print(f"Ataques de {attacker.name}:")
            atk_labels = [
                f"{atk.name} ({atk.attack_type}) — Custo: {atk.cost}⚡ — Valor: {atk.value}"
                for atk in attacker.attacks
            ]
            atk_idx = pick_index("Qual ataque?", atk_labels)
            attack = attacker.attacks[atk_idx]
            t_type = attack.attack_type.strip().lower()

            target_indices = []
            if t_type == "single":
                opp_alive = opp.alive_active()
                if not opp_alive:
                    print("Oponente sem animatronics ativos.")
                    continue
                t_idx = pick_index("Atacar qual animatronic do oponente?", opp_alive)
                target_indices = [opp.active.index(opp_alive[t_idx])]
            elif t_type == "stall":
                opp_alive = opp.alive_active()
                if not opp_alive:
                    print("Oponente sem animatronics ativos.")
                    continue
                t_idx = pick_index("Dar stall em qual animatronic?", opp_alive)
                target_indices = [opp.active.index(opp_alive[t_idx])]
            elif t_type == "heal":
                own_alive = p.alive_active()
                if own_alive:
                    if yes_no("Curar um animatronic específico?"):
                        idx = pick_index("Curar qual?", own_alive)
                        target_indices = [p.active.index(own_alive[idx])]

            success = game.do_attack(a_idx, atk_idx, target_indices)
            if success:
                attacked_indices.add(a_idx)

        elif choice == "4":
            supports = p.supports_in_hand()
            if not supports:
                print("Sem suportes na mão.")
                continue
            idx = pick_index("Usar qual suporte?", supports)
            game.do_use_support(supports[idx])

        elif choice == "5":
            all_anim = p.active + p.animatronics_in_hand()
            if not all_anim:
                continue
            idx = pick_index("Ver detalhes de qual animatronic?", all_anim)
            a = all_anim[idx]
            print(f"\n{'─'*40}")
            print(f"  {a.name}")
            print(f"  HP: {a.current_hp}/{a.max_hp}  ⚡: {a.electricity}/{a.max_electricity}")
            for atk in a.attacks:
                print(f"  • {atk.name} [{atk.attack_type}] custo:{atk.cost} val:{atk.value}")
            print(f"{'─'*40}")
        else:
            print("Opção inválida.")


# ── AI Opponent ───────────────────────────────────────────────────────────────

def run_ai_turn(game):
    """Simple AI turn."""
    import random
    p = game.current_player()
    opp = game.opponent()
    print(f"\n[IA] Turno de {p.name}...")

    # Place animatronics if possible
    for card in p.animatronics_in_hand():
        if len(p.active) < 4:
            p.place_animatronic(card)
            game.log(f"[IA] {p.name} coloca {card.name} na party.")

    # Attach electricity to first active with room
    if not p.has_attached_electricity and p.electricity_in_hand() > 0:
        for a in p.active:
            if a.electricity < a.max_electricity:
                p.attach_electricity(a)
                game.log(f"[IA] Attachou eletricidade a {a.name}.")
                break

    # Attack if possible
    if not (game.round == 1 and game.turn == game.first_player):
        for attacker in p.alive_active():
            if not attacker.can_attack():
                continue
            for i, atk in enumerate(attacker.attacks):
                if attacker.electricity >= atk.cost:
                    t_type = atk.attack_type.strip().lower()
                    target_indices = []
                    if t_type in ("single", "stall") and opp.alive_active():
                        t = random.choice(opp.alive_active())
                        target_indices = [opp.active.index(t)]
                    a_idx = p.active.index(attacker)
                    game.do_attack(a_idx, i, target_indices)
                    break

    # Use supports randomly
    for s in p.supports_in_hand():
        if random.random() < 0.4:
            game.do_use_support(s)
            break