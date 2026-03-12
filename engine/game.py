"""
FNAF TCG - Game Engine
"""
import random
from engine.cards import AnimatronicCard, SupportCard, ElectricityCard
from engine.player import Player
from engine.combat import resolve_attack

POINTS_TO_WIN = 4


class Game:
    def __init__(self, p1: Player, p2: Player):
        self.players = [p1, p2]
        self.turn = 0          # which player's turn (0 or 1)
        self.round = 1
        self.first_player = 0  # decided by dice
        self.game_over = False
        self.winner: Player | None = None
        self._log: list[str] = []

    # ── Logging ──────────────────────────────────────────────────────────────

    def log(self, msg: str):
        self._log.append(msg)
        print(msg)

    def flush_log(self) -> list[str]:
        out = self._log[:]
        self._log.clear()
        return out

    # ── Setup ─────────────────────────────────────────────────────────────────

    def roll_for_first(self) -> int:
        """Roll dice for both players. Returns index of first player."""
        rolls = [random.randint(1, 6), random.randint(1, 6)]
        while rolls[0] == rolls[1]:
            rolls = [random.randint(1, 6), random.randint(1, 6)]
        first = 0 if rolls[0] > rolls[1] else 1
        self.log(f"Dado: {self.players[0].name}={rolls[0]}, {self.players[1].name}={rolls[1]}")
        self.log(f"{self.players[first].name} escolhe se vai primeiro ou segundo!")
        self.first_player = first
        return first

    def setup(self):
        """Draw opening hands, handle mulligans."""
        mulligans = [0, 0]
        for i, p in enumerate(self.players):
            m = p.setup_opening_hand()
            mulligans[i] = m
            if m > 0:
                self.log(f"{p.name} teve {m} mulligan(s).")

        # Opponent draws +1 if they had none and the other did
        for i in range(2):
            opp = 1 - i
            if mulligans[i] > 0 and mulligans[opp] == 0:
                extra = self.players[opp].draw(1)
                self.log(f"{self.players[opp].name} tira 1 carta extra (Mulligan bonus).")

    # ── Turn Structure ────────────────────────────────────────────────────────

    def start_turn(self):
        p = self.current_player()
        p.start_turn()
        # Draw 1 at start of turn (after first turn)
        if self.round > 1 or self.turn != self.first_player:
            p.draw(1)
        self.log(f"\n{'='*50}")
        self.log(f"Turno de {p.name} (Rodada {self.round})")
        self.log(f"{'='*50}")

    def end_turn(self):
        self._check_win_conditions()
        self.turn = 1 - self.turn
        if self.turn == self.first_player:
            self.round += 1

    def current_player(self) -> Player:
        return self.players[self.turn]

    def opponent(self) -> Player:
        return self.players[1 - self.turn]

    # ── Win Conditions ────────────────────────────────────────────────────────

    def _check_win_conditions(self):
        for i, p in enumerate(self.players):
            opp = self.players[1 - i]
            # Remove dead animatronics
            dead = opp.remove_dead()
            if dead:
                for d in dead:
                    self.log(f"{d.name} foi derrotado!")

            # Point from KO'd all active animatronics
            if len(opp.alive_active()) == 0 and len(opp.active) == 0:
                if len(opp.animatronics_in_hand()) == 0 and all(
                    not isinstance(c, AnimatronicCard) for c in opp.deck
                ):
                    # No animatronics left anywhere = win game
                    self.log(f"{p.name} acabou com todos os animatronics de {opp.name}! VITÓRIA IMEDIATA!")
                    self.game_over = True
                    self.winner = p
                    return
                else:
                    p.points += 1
                    self.log(f"{p.name} ganha 1 ponto! (Total: {p.points})")
                    # Refill opponent active from hand
                    for card in opp.animatronics_in_hand():
                        if len(opp.active) < 4:
                            opp.hand.remove(card)
                            opp.active.append(card)

            if p.points >= POINTS_TO_WIN:
                self.log(f"{p.name} chegou a {POINTS_TO_WIN} pontos! VITÓRIA!")
                self.game_over = True
                self.winner = p
                return

        # Remove dead from opponent again after possible refill
        for p in self.players:
            p.remove_dead()

    # ── Actions ──────────────────────────────────────────────────────────────

    def do_attack(self, attacker_idx: int, attack_idx: int, target_indices: list[int]) -> bool:
        """Perform an attack. attacker_idx in current player's active."""
        p = self.current_player()
        opp = self.opponent()

        if attacker_idx >= len(p.active):
            self.log("Índice de atacante inválido.")
            return False
        attacker = p.active[attacker_idx]

        if attack_idx >= len(attacker.attacks):
            self.log("Índice de ataque inválido.")
            return False
        attack = attacker.attacks[attack_idx]

        # Determine targets
        t_type = attack.attack_type.strip().lower()
        if t_type in ("single", "stall"):
            targets = [opp.active[i] for i in target_indices if i < len(opp.active)]
        elif t_type == "multi":
            targets = opp.alive_active()  # hits all
        elif t_type == "heal":
            if target_indices:
                targets = [p.active[i] for i in target_indices if i < len(p.active)]
            else:
                targets = p.active[:]
        else:
            targets = []

        # First-turn restriction
        if self.round == 1 and self.turn == self.first_player:
            self.log(f"O primeiro jogador não pode atacar no primeiro turno!")
            return False

        logs = resolve_attack(attacker, attack, targets, p.active)
        for l in logs:
            self.log(l)

        self._check_win_conditions()
        return True

    def do_place_animatronic(self, hand_idx: int) -> bool:
        p = self.current_player()
        anim_hand = p.animatronics_in_hand()
        if hand_idx >= len(anim_hand):
            return False
        card = anim_hand[hand_idx]
        if p.place_animatronic(card):
            self.log(f"{p.name} coloca {card.name} na party!")
            return True
        self.log("Não podes colocar mais animatronics (máximo 4).")
        return False

    def do_attach_electricity(self, active_idx: int) -> bool:
        p = self.current_player()
        if active_idx >= len(p.active):
            return False
        if p.attach_electricity(p.active[active_idx]):
            self.log(f"⚡ Eletricidade attachada a {p.active[active_idx].name}!")
            return True
        self.log("Não podes attchar eletricidade agora.")
        return False

    def do_use_support(self, support: SupportCard) -> bool:
        p = self.current_player()
        return p.use_support(support, self, self.turn)
