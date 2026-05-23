# Cardagon

## Cards

### Units

Damage = ATK (of the attacker) / DEF (of the attacked)

Order:

1. Movement
2. Attacking
3. After attacking no more movement
4. Unit moves onto field of defeated unit

- Swordsman (15 gold)
  - HP: 20
  - ATK: 10
  - DEF: 1.5
  - MOV: 1
  - RNG: 1
- Archer (15 gold)
  - HP: 15
  - ATK: 5
  - DEF: 1
  - MOV: 1
  - RNG: 2
- Knight (30 gold)
  - HP: 15
  - ATK: 10
  - DEF: 1.5
  - MOV: 2
  - RNG: 1
- Settler (20 gold)
  - HP: 6
  - ATK: 0
  - DEF: 1
  - MOV: 1
  - RNG: 0

### Buildings

Can only be built on your own tiles

- Campfire
  - Starting tile
  - Can't be gotten as a card
- Goldmine (20 gold)
  - Gives 5 gold every turn
- Tower (35 gold)
  - Affects the unit standing on its field
    - Defense
    - Damage
- Infirmary (25 gold)
  - Heals 50% of lost life

### Spells

Spells are active for a limited number of turns

- Increased taxes (1/2 of income)
  - Active: 3 turns
  - Increases own gold per turn by 25%
- Thunderstorm (20 Gold)
  - Active: 1 Zug
  - Does 5 damage
  - Damage area: radius 2

## Every turn

1. Receive gold
   1. Anhand folgender Aspekte wird Gold erhalten
      1. Besetzte Felder, pro Feld 3 Gold
      2. Was auf den Feldern gebaut wurde
      3. Effekt-Karten

- Karten Kaufen
- Jede Karte darf nur einmal gekauft werden
- Karten einsetzen
  - Gesetzte Karten werden erst im nächsten Zug aktiv
- Truppen bewegen
- Gegnerische Felder können vom Siedler übernommen werden
- Gegnerisches Startfeld kann von jeglicher Truppe übetnommen werden, 1 Zug nach draufgehen

## Spielziel

- Domination

## Spielfeld

- Hexagon
  - Flachland
  - Angeordnet in einem Hexagon
  - Seitenlänge 5 (Muss durch Playtesting herausgefunden werden)
- 2x random Startposition
  - Nicht auf dem Äussersten Ring
  - Nicht auf den 3 innersten Ringen
  - Min. 3 Felder zwischen den Startpunkten
  - Start mit allen Feldern rundherum (7 Felder)
## Future

- Fog of War
- Terrain
  - Flachland
  - Berge
  - Wasser
  - Wald
  - Wüste
  - Movement penalty
