"""
FNAF TCG - Combat Resolution
"""
from engine.cards import AnimatronicCard, Attack


def resolve_attack(
    attacker: AnimatronicCard,
    attack: Attack,
    targets: list[AnimatronicCard],
    player_active: list[AnimatronicCard],
) -> list[str]:
    """
    Execute an attack. Modifies HP/stall in place.
    Returns list of log messages.
    """
    logs = []

    if not attacker.can_attack():
        logs.append(f"{attacker.name} está em stall e não pode atacar!")
        return logs

    if not attacker.spend_electricity(attack.cost):
        logs.append(f"{attacker.name} não tem eletricidade suficiente ({attack.cost} necessário).")
        return logs

    t_type = attack.attack_type.strip().lower()

    if t_type == "single":
        if len(targets) != 1:
            logs.append("Single Target requer exatamente 1 alvo.")
            return logs
        t = targets[0]
        # Check Freddy Mask protection
        if getattr(t, "_freddy_mask", False) and _is_toy_or_withered(attacker):
            logs.append(f"{attacker.name} ataca {t.name}, mas a Freddy Mask bloqueia!")
            t._freddy_mask = False
            return logs
        t.take_damage(attack.value)
        logs.append(f"{attacker.name} usa {attack.name} em {t.name} — {attack.value} dano!")

        # Special: Puppet Strings Attached = stall
        if attack.name == "Strings Attached":
            t.stalled_turns += 3
            logs.append(f"  {t.name} fica em stall por 3 turnos!")

    elif t_type == "multi":
        if not targets:
            logs.append("Nenhum alvo para Multi Target.")
            return logs
        for t in targets:
            if getattr(t, "_freddy_mask", False) and _is_toy_or_withered(attacker):
                logs.append(f"  {t.name} está protegida pela Freddy Mask!")
                t._freddy_mask = False
                continue
            t.take_damage(attack.value)
            logs.append(f"  {t.name} recebe {attack.value} dano de {attack.name}!")

    elif t_type == "heal":
        if len(targets) == 1:
            targets[0].heal(attack.value)
            logs.append(f"{attacker.name} usa {attack.name} — cura {attack.value} HP em {targets[0].name}!")
        else:
            for t in player_active:
                t.heal(attack.value)
            logs.append(f"{attacker.name} usa {attack.name} — cura {attack.value} HP em toda a party!")

    elif t_type == "stall":
        if not targets:
            logs.append("Nenhum alvo para Stall.")
            return logs
        for t in targets:
            t.stalled_turns += attack.value if attack.value > 0 else 1
            logs.append(f"{attacker.name} usa {attack.name} em {t.name} — stall por {t.stalled_turns} turno(s)!")

    else:
        logs.append(f"Tipo de ataque desconhecido: {attack.attack_type}")

    return logs


def _is_toy_or_withered(card: AnimatronicCard) -> bool:
    return "Toy" in card.name or "Withered" in card.name
