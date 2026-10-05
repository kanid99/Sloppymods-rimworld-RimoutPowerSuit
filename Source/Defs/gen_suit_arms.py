"""Writes Defs/ThingDefs/SuitArms.xml: the arm modules, their guns, projectiles and effects.
Run from the repository root: python3 Source/Defs/gen_suit_arms.py. Edit the tables here, not the XML."""
from xml.sax.saxutils import escape

SUIT = {'Bulwark': 'RPS_PowerSuitFrame', 'Bughunter': 'RPS_PowerSuitBughunter', 'Miner': 'RPS_PowerSuitMiner', 'Builder': 'RPS_PowerSuitBuilder'}

# projectile: (label, texture, damageDef, damage, armour penetration, speed, explosion radius or None)
PROJ = {
    'Minigun':    ('minigun slug', 'Slug', 'Bullet', 9, 0.20, 70, None),
    'Autocannon': ('autocannon shell', 'Slug', 'Bullet', 28, 0.50, 80, None),
    'Laser':      ('laser bolt', 'Laser', 'Burn', 17, 0.45, 140, None),
    'Rocket':     ('rocket', 'Rocket', 'Bomb', 40, None, 45, 1.9),
    'Grenade':    ('grenade', 'Grenade', 'Bomb', 25, None, 30, 1.9),
    'Arc':        ('arc charge', 'Arc', 'EMP', 30, None, 35, 1.5),
    'Flame':      ('flame', 'Flame', 'Flame', 9, 0.10, 28, None),
    'FuelFlame':  ('injected flame', 'Flame', 'Flame', 13, 0.15, 32, None),
    'Nail':       ('nail', 'Slug', 'Bullet', 8, 0.15, 70, None),
}

# gun: (label, projectile, warmup, range, burst, ticks between shots, cooldown, sound, tail, forced miss radius, targets ground)
GUNS = {
    'Minigun':    ('arm minigun', 'Minigun', 1.5, 26.9, 20, 4, 2.0, 'Shot_Minigun', 'GunTail_Heavy', None, False),
    'Autocannon': ('arm autocannon', 'Autocannon', 2.2, 31.9, 3, 12, 2.4, 'Shot_Minigun', 'GunTail_Heavy', None, False),
    'Laser':      ('arm laser', 'Laser', 1.6, 29.9, 2, 10, 1.8, 'Shot_ChargeRifle', None, None, False),
    'Rockets':    ('arm rocket pod', 'Rocket', 2.5, 29.9, 3, 15, 3.5, 'Shot_TripleRocket', None, 2.5, True),
    'Grenade':    ('arm grenade launcher', 'Grenade', 1.8, 21.9, 1, 0, 2.6, 'Shot_IncendiaryLauncher', None, 1.9, True),
    'Arc':        ('arm arc projector', 'Arc', 1.8, 19.9, 1, 0, 2.6, 'Shot_IncendiaryLauncher', None, 1.5, True),
    'Flamer':     ('arm flamer', 'Flame', 1.2, 8.9, 6, 5, 2.2, 'Shot_IncendiaryLauncher', None, None, True),
    'FuelFlamer': ('fuel-injected arm flamer', 'FuelFlame', 1.2, 11.9, 8, 5, 2.0, 'Shot_IncendiaryLauncher', None, None, True),
    'NailGun':    ('arm nail gun', 'Nail', 0.9, 15.9, 4, 6, 1.4, 'Shot_Autopistol', None, None, False),
}

TOOL = '''          <li>
            <label>{label}</label>
            <capacities>
              <li>{cap}</li>
            </capacities>
            <power>{power}</power>
            <cooldownTime>{cd}</cooldownTime>
            <armorPenetration>{ap}</armorPenetration>{extra}
          </li>'''
# melee hediffs: (label, description, tool label, capacity, power, cooldown, AP, (extra damage def, amount) or None)
MELEE = {
    'Hammer':      ('hammer arm', 'A heavy hammer built into a suit arm.', 'hammer', 'Blunt', 30, 2.6, 0.40, ('Stun', 14)),
    'Chainsaw':    ('chainsaw arm', 'A chainsaw built into a suit arm.', 'chainsaw', 'Cut', 26, 2.0, 0.35, None),
    'PowerHammer': ('pneumatic power hammer arm', 'A hammer driven by a pneumatic pressure system.', 'power hammer', 'Blunt', 40, 2.4, 0.50, ('Stun', 22)),
}

# arm modules: key -> (suit, texKey, label, description, gun, hediff, cost, extra fields)
C_GUN = dict(Steel=80, Plasteel=25, ComponentIndustrial=4)
C_HI = dict(Steel=80, Plasteel=35, ComponentIndustrial=4, ComponentSpacer=1)
C_MELEE = dict(Steel=90, Plasteel=20, ComponentIndustrial=3)
ARMS = [
    ('Bulwark', 'minigun', 'Bulwark minigun arm', 'A rotary gun on a Bulwark arm. Becomes the pilot\'s weapon; two minigun arms fire as one.', 'Minigun', None, C_GUN, {}),
    ('Bulwark', 'autocannon', 'Bulwark autocannon arm', 'A heavy autocannon on a Bulwark arm. Becomes the pilot\'s weapon.', 'Autocannon', None, C_HI, {}),
    ('Bulwark', 'laser', 'Bulwark laser arm', 'A laser on a Bulwark arm: burning bolts that cut through armour. Becomes the pilot\'s weapon.', 'Laser', None, C_HI, {}),
    ('Bulwark', 'rockets', 'Bulwark rocket pod arm', 'A rocket pod on a Bulwark arm: volleys of explosive rockets. Becomes the pilot\'s weapon.', 'Rockets', None, dict(Steel=90, Plasteel=25, ComponentIndustrial=5), {}),
    ('Bulwark', 'grenade', 'Bulwark grenade launcher arm', 'A grenade launcher on a Bulwark arm. Becomes the pilot\'s weapon.', 'Grenade', None, C_GUN, {}),
    ('Bulwark', 'arc', 'Bulwark arc projector arm', 'Throws electric arc charges that disable machines and shields. Becomes the pilot\'s weapon.', 'Arc', None, C_HI, {}),
    ('Bulwark', 'flamer', 'Bulwark flamer arm', 'A short-range flamethrower on a Bulwark arm. Becomes the pilot\'s weapon.', 'Flamer', None, dict(Steel=80, Plasteel=20, ComponentIndustrial=3, Chemfuel=30), {}),
    ('Bulwark', 'hammer', 'Bulwark hammer arm', 'A heavy hammer on a Bulwark arm: crushing, stunning blows up close.', None, 'Hammer', C_MELEE, {}),
    ('Bulwark', 'chainsaw', 'Bulwark chainsaw arm', 'A chainsaw on a Bulwark arm: deep cuts up close.', None, 'Chainsaw', C_MELEE, {}),
    ('Bulwark', 'towershield', 'Bulwark tower shield arm', 'A huge shield held up in front of the suit, from shoulder to feet. Much harder to hurt, a little slower.', None, 'TowerShield', dict(Steel=60, Plasteel=60, ComponentIndustrial=1),
     {'pairTexKey': 'towershield_pair', 'aboveHelmetSouth': 'true'}),
    ('Bughunter', 'flamer', 'Bughunter fuel-injected flamer arm', 'A flamethrower fed by the shoulder plate\'s fuel-injection system: longer range and hotter flames than a plain flamer. Becomes the pilot\'s weapon.', 'FuelFlamer', None, dict(Steel=80, Plasteel=25, ComponentIndustrial=4, Chemfuel=40), {}),
    ('Miner', 'drill', 'Miner drill arm', 'A heavy rotary drill on a Miner arm: the pilot digs through rock much faster, and two drill arms faster still. It bores into anything that gets too close, too.', None, 'Drill', dict(Steel=90, Plasteel=15, ComponentIndustrial=3), {}),
    ('Builder', 'combo', 'Builder construction drill arm', 'A construction drill with a nail gun mounted alongside, on a Builder arm. The drill speeds up building (two arms faster still); the nail gun becomes the pilot\'s weapon, a short-range rapid-fire gun.', 'NailGun', 'ConstructionDrill', dict(Steel=90, Plasteel=15, ComponentIndustrial=4), {}),
    ('Bughunter', 'hammer', 'Bughunter power hammer arm', 'A hammer driven by the shoulder plate\'s pneumatic pressure system: brutal, stunning blows up close.', None, 'PowerHammer', dict(Steel=90, Plasteel=30, ComponentIndustrial=4), {}),
]


def gun_def(key, twin=False):
    label, proj, warm, rng, burst, tbs, cd, snd, tail, miss, ground = GUNS[key]
    name = f'RPS_ArmGun_{key}' + ('_Twin' if twin else '')
    if twin:
        label = 'twin ' + label.replace('arm ', 'arm ') + 's'
        burst = burst * 2 if burst > 1 else 2
        tbs = tbs or 8
    icon = next(f'Things/Item/PowerSuit/Arms/{s}_{t}' for s, t, _, _, g, _, _, _ in ARMS if g == key)
    lines = [f'  <ThingDef ParentName="RPS_ArmGunBase">',
             f'    <defName>{name}</defName>',
             f'    <label>{escape(label)}</label>',
             f'    <description>A suit arm\'s gun. It exists only while a pilot is in the suit.</description>',
             f'    <uiIconPath>{icon}</uiIconPath>',
             f'    <statBases>',
             f'      <RangedWeapon_Cooldown>{cd}</RangedWeapon_Cooldown>',
             f'    </statBases>',
             f'    <verbs>', f'      <li>',
             f'        <verbClass>Verb_Shoot</verbClass>',
             f'        <hasStandardCommand>true</hasStandardCommand>',
             f'        <defaultProjectile>RPS_Projectile_{proj}</defaultProjectile>',
             f'        <warmupTime>{warm}</warmupTime>',
             f'        <range>{rng}</range>',
             f'        <burstShotCount>{burst}</burstShotCount>']
    if burst > 1:
        lines.append(f'        <ticksBetweenBurstShots>{tbs}</ticksBetweenBurstShots>')
    lines.append(f'        <soundCast>{snd}</soundCast>')
    if tail:
        lines.append(f'        <soundCastTail>{tail}</soundCastTail>')
    lines.append(f'        <muzzleFlashScale>9</muzzleFlashScale>')
    if miss:
        lines += [f'        <forcedMissRadius>{miss}</forcedMissRadius>', f'        <ai_AvoidFriendlyFireRadius>3</ai_AvoidFriendlyFireRadius>']
    if ground:
        lines += ['        <targetParams>', '          <canTargetLocations>true</canTargetLocations>', '        </targetParams>']
    lines += ['      </li>', '    </verbs>', '  </ThingDef>']
    return '\n'.join(lines)


def proj_def(key):
    label, tex, dmg, amount, ap, speed, radius = PROJ[key]
    lines = [f'  <ThingDef ParentName="BaseBullet">',
             f'    <defName>RPS_Projectile_{key}</defName>',
             f'    <label>{label}</label>']
    if radius:
        lines.append('    <thingClass>Projectile_Explosive</thingClass>')
    lines += ['    <graphicData>', f'      <texPath>Things/Projectile/PowerSuit/{tex}</texPath>',
              '      <graphicClass>Graphic_Single</graphicClass>', '      <shaderType>TransparentPostLight</shaderType>', '    </graphicData>',
              '    <projectile>', f'      <damageDef>{dmg}</damageDef>', f'      <damageAmountBase>{amount}</damageAmountBase>']
    if ap is not None:
        lines.append(f'      <armorPenetrationBase>{ap}</armorPenetrationBase>')
    lines.append(f'      <speed>{speed}</speed>')
    if radius:
        lines += [f'      <explosionRadius>{radius}</explosionRadius>', '      <flyOverhead>false</flyOverhead>']
    lines += ['    </projectile>', '  </ThingDef>']
    return '\n'.join(lines)


def melee_hediff(key):
    label, desc, tl, cap, power, cd, ap, extra = MELEE[key]
    ex = ''
    if extra:
        ex = f'\n            <extraMeleeDamages>\n              <li>\n                <def>{extra[0]}</def>\n                <amount>{extra[1]}</amount>\n              </li>\n            </extraMeleeDamages>'
    return f'''  <HediffDef ParentName="RPS_SuitArmHediffBase">
    <defName>RPS_Arm{key}</defName>
    <label>{label}</label>
    <description>{escape(desc)} Its strikes join the pilot's melee attacks while they are in the suit.</description>
    <comps>
      <li Class="HediffCompProperties_VerbGiver">
        <tools>
{TOOL.format(label=tl, cap=cap, power=power, cd=cd, ap=ap, extra=ex)}
        </tools>
      </li>
    </comps>
  </HediffDef>'''


def arm_def(suit, tex, label, desc, gun, hediff, cost, extra):
    name = f'RPS_Arm_{suit}_{tex}'
    lines = [f'  <ThingDef ParentName="RPS_SuitArmBase">', f'    <defName>{name}</defName>', f'    <label>{escape(label)}</label>',
             f'    <description>{escape(desc)}\\n\\nFits only a {suit}: right-click a standing {suit} with a colonist selected to fit it to the left or right arm.</description>',
             '    <graphicData>', f'      <texPath>Things/Item/PowerSuit/Arms/{suit}_{tex}</texPath>', '    </graphicData>',
             '    <costList>'] + [f'      <{k}>{v}</{k}>' for k, v in cost.items()] + ['    </costList>',
             '    <modExtensions>', '      <li Class="RimoutPowerSuit.ArmModuleExtension">',
             f'        <suits>', f'          <li>{SUIT[suit]}</li>', f'        </suits>', f'        <texKey>{tex}</texKey>']
    if gun:
        lines.append(f'        <gun>RPS_ArmGun_{gun}</gun>')
        lines.append(f'        <twinGun>RPS_ArmGun_{gun}_Twin</twinGun>')
    if hediff:
        lines.append(f'        <hediff>RPS_Arm{hediff}</hediff>')
    lines += [f'        <{k}>{v}</{k}>' for k, v in extra.items()]
    lines += ['      </li>', '    </modExtensions>', '  </ThingDef>']
    return '\n'.join(lines)


HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<!-- Generated by Source/Defs/gen_suit_arms.py: edit the tables there, then re-run it. -->
<Defs>

  <!-- Arm modules: items fitted to a standing suit's left or right arm (JobDriver_FitSuitArm).
       Each fits one suit. A gun arm becomes the pilot's weapon while they are inside; a melee
       arm adds its strikes; the tower shield adds armour. See SuitArmUtility. -->
  <ThingDef Name="RPS_SuitArmBase" Abstract="True">
    <thingClass>ThingWithComps</thingClass>
    <category>Item</category>
    <drawerType>MapMeshOnly</drawerType>
    <altitudeLayer>Item</altitudeLayer>
    <selectable>true</selectable>
    <alwaysHaulable>true</alwaysHaulable>
    <useHitPoints>true</useHitPoints>
    <pathCost>14</pathCost>
    <stackLimit>1</stackLimit>
    <tickerType>Never</tickerType>
    <techLevel>Spacer</techLevel>
    <thingCategories>
      <li>Manufactured</li>
    </thingCategories>
    <graphicData>
      <graphicClass>Graphic_Single</graphicClass>
      <drawSize>(1.1,1.1)</drawSize>
    </graphicData>
    <statBases>
      <MaxHitPoints>150</MaxHitPoints>
      <Mass>18</Mass>
      <WorkToMake>14000</WorkToMake>
      <Flammability>0.2</Flammability>
      <DeteriorationRate>1</DeteriorationRate>
    </statBases>
    <comps>
      <li Class="CompProperties_Forbiddable" />
    </comps>
    <recipeMaker>
      <unfinishedThingDef>UnfinishedTechArmor</unfinishedThingDef>
      <researchPrerequisite>RPS_PowerSuits</researchPrerequisite>
      <workSpeedStat>GeneralLaborSpeed</workSpeedStat>
      <workSkill>Crafting</workSkill>
      <effectWorking>Smith</effectWorking>
      <soundWorking>Recipe_Machining</soundWorking>
      <skillRequirements>
        <Crafting>6</Crafting>
      </skillRequirements>
      <recipeUsers>
        <li>FabricationBench</li>
      </recipeUsers>
      <displayPriority>210</displayPriority>
    </recipeMaker>
  </ThingDef>

  <!-- Arm guns: the pilot's weapon while they are in a suit with a gun arm. Never dropped
       (HarmonyPatches); made and destroyed in code. Not drawn in the pilot's hands: the arm is. -->
  <ThingDef Name="RPS_ArmGunBase" Abstract="True">
    <thingClass>ThingWithComps</thingClass>
    <category>Item</category>
    <equipmentType>Primary</equipmentType>
    <drawerType>MapMeshOnly</drawerType>
    <altitudeLayer>Item</altitudeLayer>
    <useHitPoints>false</useHitPoints>
    <selectable>true</selectable>
    <destroyOnDrop>true</destroyOnDrop>
    <tradeability>None</tradeability>
    <techLevel>Spacer</techLevel>
    <relicChance>0</relicChance>
    <graphicData>
      <texPath>Things/Item/PowerSuit/ArmGunHidden</texPath>
      <graphicClass>Graphic_Single</graphicClass>
    </graphicData>
    <statBases>
      <Mass>0</Mass>
      <AccuracyTouch>0.70</AccuracyTouch>
      <AccuracyShort>0.66</AccuracyShort>
      <AccuracyMedium>0.58</AccuracyMedium>
      <AccuracyLong>0.45</AccuracyLong>
    </statBases>
    <comps>
      <li>
        <compClass>CompEquippable</compClass>
      </li>
    </comps>
    <modExtensions>
      <li Class="RimoutPowerSuit.ArmGunExtension" />
    </modExtensions>
  </ThingDef>

  <HediffDef Name="RPS_SuitArmHediffBase" Abstract="True">
    <hediffClass>HediffWithComps</hediffClass>
    <defaultLabelColor>(0.75, 0.85, 1)</defaultLabelColor>
    <isBad>false</isBad>
    <scenarioCanAdd>false</scenarioCanAdd>
  </HediffDef>
'''

SHIELD = '''  <HediffDef ParentName="RPS_SuitArmHediffBase">
    <defName>RPS_ArmTowerShield</defName>
    <label>tower shield arm</label>
    <description>A huge shield held up in front of the suit: much harder to hurt, a little slower.</description>
    <stages>
      <li>
        <statOffsets>
          <ArmorRating_Sharp>0.35</ArmorRating_Sharp>
          <ArmorRating_Blunt>0.25</ArmorRating_Blunt>
          <MoveSpeed>-0.15</MoveSpeed>
        </statOffsets>
      </li>
    </stages>
  </HediffDef>'''

CONSTRUCTION = '''  <HediffDef ParentName="RPS_SuitArmHediffBase">
    <defName>RPS_ArmConstructionDrill</defName>
    <label>construction drill arm</label>
    <description>A construction drill on a suit arm: much faster building. Two arms build faster still.</description>
    <initialSeverity>1</initialSeverity>
    <maxSeverity>2</maxSeverity>
    <stages>
      <li>
        <label>one drill</label>
        <statOffsets>
          <ConstructionSpeed>0.35</ConstructionSpeed>
        </statOffsets>
      </li>
      <li>
        <minSeverity>1.5</minSeverity>
        <label>two drills</label>
        <statOffsets>
          <ConstructionSpeed>0.7</ConstructionSpeed>
        </statOffsets>
      </li>
    </stages>
  </HediffDef>'''

DRILL = '''  <HediffDef ParentName="RPS_SuitArmHediffBase">
    <defName>RPS_ArmDrill</defName>
    <label>drill arm</label>
    <description>A heavy rotary drill on a suit arm: much faster digging, and a boring strike up close. Two drill arms dig faster still.</description>
    <initialSeverity>1</initialSeverity>
    <maxSeverity>2</maxSeverity>
    <stages>
      <li>
        <label>one drill</label>
        <statOffsets>
          <MiningSpeed>0.4</MiningSpeed>
        </statOffsets>
      </li>
      <li>
        <minSeverity>1.5</minSeverity>
        <label>two drills</label>
        <statOffsets>
          <MiningSpeed>0.8</MiningSpeed>
        </statOffsets>
      </li>
    </stages>
    <comps>
      <li Class="HediffCompProperties_VerbGiver">
        <tools>
          <li>
            <label>drill</label>
            <capacities>
              <li>Stab</li>
            </capacities>
            <power>20</power>
            <cooldownTime>2.2</cooldownTime>
            <armorPenetration>0.5</armorPenetration>
          </li>
        </tools>
      </li>
    </comps>
  </HediffDef>'''

if __name__ == '__main__':
    parts = [HEADER]
    parts += [arm_def(*a) for a in ARMS]
    for g in GUNS:
        parts += [gun_def(g), gun_def(g, twin=True)]
    parts += [proj_def(p) for p in PROJ]
    parts += [melee_hediff(m) for m in MELEE] + [SHIELD, DRILL, CONSTRUCTION]
    open('Defs/ThingDefs/SuitArms.xml', 'w').write('\n\n'.join(parts) + '\n\n</Defs>\n')
    print('wrote Defs/ThingDefs/SuitArms.xml')
