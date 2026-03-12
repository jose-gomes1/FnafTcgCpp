# FNAF TCG — Five Nights at Freddy's Trading Card Game

Implementação em Python do jogo de cartas colecionáveis baseado no universo FNAF.

## Estrutura de Ficheiros

```
fnaf_tcg/
├── main.py              ← Jogo principal
├── deck_builder.py      ← Construtor de decks
├── data/
│   ├── animatronics.csv ← Dados de todos os animatronics
│   └── supports.csv     ← Dados de todos os suportes
├── engine/
│   ├── cards.py         ← Modelos de dados das cartas
│   ├── deck.py          ← Validação e construção de decks
│   ├── player.py        ← Estado do jogador + efeitos de suporte
│   ├── combat.py        ← Resolução de combate
│   └── game.py          ← Motor principal do jogo
├── ui/
│   └── cli.py           ← Interface de linha de comandos
└── decks/               ← Decks guardados (criado automaticamente)
```

## Como Jogar

```bash
python main.py
```

Escolhe entre:
- **Jogador vs IA** — joga contra uma IA simples
- **Jogador vs Jogador** — pass-and-play no mesmo computador

## Construtor de Deck

```bash
python deck_builder.py
```

### Comandos do Deck Builder

| Comando | Descrição |
|---|---|
| `browse anim [filtro]` | Ver todos os animatronics |
| `browse sup [filtro]` | Ver todos os suportes |
| `add <nome> [qty]` | Adicionar carta ao deck |
| `add elec [qty]` | Adicionar eletricidades |
| `remove <nome> [qty]` | Remover carta |
| `show` | Ver deck atual |
| `validate` | Verificar se o deck é válido |
| `save` | Guardar deck em JSON |
| `load` | Carregar deck guardado |
| `rename <nome>` | Renomear deck |
| `new` | Começar deck novo |
| `help` | Mostrar ajuda |

**Exemplo:**
```
> browse anim Nightmare
> add Nightmare Freddy 2
> add Nightmare Bonnie 2
> add elec 15
> validate
> save
```

## Deck Inicial (Padrão)

| Quantidade | Carta |
|---|---|
| 3× | Withered Freddy |
| 2× | Shadow Freddy |
| 2× | Jack-O-Bonnie |
| 2× | Jack-O-Chica |
| 3× | Freddy Mask |
| 3× | William Afton |
| 3× | Power Drain |
| 12× | Eletricidade |

## Regras Resumidas

- **Objetivo:** Primeiro a 4 pontos ganha
- **Ponto:** Eliminar todos os animatronics ativos do oponente
- **Vitória imediata:** Eliminar TODOS os animatronics do oponente
- **Party:** Máximo 4 animatronics ativos
- **Eletricidade:** 1 por turno da mão para animatronic ativo
- **Primeiro turno:** O primeiro jogador não pode atacar
- **Mulligans:** Até 3 (sem animatronic na mão inicial)

## Tipos de Ataque

| Tipo | Efeito |
|---|---|
| Single | Ataca 1 animatronic do oponente |
| Multi | Ataca todos os animatronics do oponente |
| Heal | Cura animatronic(s) próprios |
| Stall | Impede animatronic de atacar por X turnos |
