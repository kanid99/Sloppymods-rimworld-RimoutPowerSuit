# Rimout Power Suit - design notes

Decisions agreed with the owner, to build from. Numbers are starting points for tuning.

## Modular suit

- Slots: **chassis** (chest + hips; defines the role and base stats), **helmet**, **left arm**,
  **right arm** (shoulder/arm armour - pawns have no arms; each arm drawn once, mirrored for the
  other side, so left and right can differ), **legs** (shown as hip/thigh plates), **back mount**.
- Lite mode: each slot is a separate worn piece, swapped anywhere. Exosuit mode: framework
  modules (core, head, mounts, attachment), swapped at bays.
- Non-combat chassis exist for hazards: vacuum, toxic gas, heat, cold. Low armour.
  Bulwark and Bughunter are the armoured ones.
- Every chassis shares one standard flat collar ring; arm pieces tuck behind it.
- Helmet lamps: a visual light cone each frame (no TPS cost), plus real light updated only when
  the pawn changes cell and only in the dark; settings: full / visual only / off.

## Role bonuses (conditional, via stat parts on the worn chassis)

- **Harvester**: plant work speed x1.5 and harvest yield +10% only when sowing, harvesting or
  cutting plants in soil - not in hydroponics basins or planters. (Optional x0.9 indoors.)
- Same pattern offered for others: Miner (mining rock), Builder (construction, not crafting),
  Medic (treating patients).

## Bughunter (insect killer)

- Focus: **heavy armour**. Bonuses to **blunt melee** (+35% blunt melee damage, any blunt
  weapon) and to **fire** (+25% flame damage dealt, any flamethrower or fire source).
- Built-in arm weapons (art: `arm_flamer`, `arm_hammer`):
  - **Hydraulic hammer arm**: a built-in heavy blunt melee attack, always available, even while
    the pilot holds a gun. Two hammer arms = more frequent hammer strikes. Drawn big and swung
    outward from its shoulder plate (which stays bolted to the chassis) so it reads at a glance.
  - **Flamethrower arm**: NOT a regular weapon - a **targeted ability button** on the pilot's
    command bar: pick a spot in range (~7 tiles), sprays a cone of fire there (reusing VFE
    Pirates' flame projectile). Cooldown; **draws its charge from the suit's power cells**
    and can't fire when they're too low. Two flamer arms = **two independent buttons**, one per
    arm, each with its own cooldown.
- **Net launcher** (chassis ability): a targeted button that fires a net over an area; insects
  caught in it are pinned (or heavily slowed) for a few seconds - other creatures are only
  slowed briefly. Sets up the hammer and flamer.
- Helmet: lamps instead of horns; no side fire port. Chassis: only a subtle hint of teeth.
- Drawbacks: **slow** (large move-speed penalty) and **power hungry** (high drain).
- Compensation: holds **two power cells** instead of one.

## Power cells

- Removable battery items carrying their own charge, charged on a powered charging rack.
- The suit drains them over time (more when drafted, moving, attacking); abilities such as the
  flamer spend charge directly. Most chassis take one cell; the Bughunter takes two.
