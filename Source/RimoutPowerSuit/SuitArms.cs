using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimoutPowerSuit
{
    public enum ArmSlot
    {
        Left,
        Right,
        // the backpack (a module whose ArmModuleExtension has back = true)
        Back
    }

    // On a suit def: its power and its built-in abilities.
    public class PowerSuitExtension : DefModExtension
    {
        // Power cells in the plain backpack; capacity = cells (charge is counted in cells).
        public int cells = 1;
        // Cells drained per day while a pilot is inside.
        public float drainPerDay = 0.5f;
        // Abilities the pilot gets from the suit itself (e.g. the Bughunter's net launcher).
        public List<AbilityDef> abilities;
        // Nets the net launcher holds (0 = no net launcher).
        public int nets;
    }

    // On an arm module or backpack item: what fitting it to a suit does.
    public class ArmModuleExtension : DefModExtension
    {
        // A backpack (fits the Back slot) rather than an arm.
        public bool back;
        // A backpack's power cells, replacing the suit's own.
        public int cells;
        // A backpack with a shield generator (Apparel_PowerSuit: the standing-still shield).
        public bool shield;
        // Abilities the pilot gets while it is fitted (e.g. the jump pack's jump).
        public List<AbilityDef> abilities;
        // Its hediff works only with an arm of this texKey fitted (the Miner's booster powers its drills).
        public string boostsArm;
        // Extra cells per day drawn while the pilot does this job (the booster while mining).
        public JobDef workJob;
        public float workDrainPerDay;
        // The suits it fits. Every suit has its own arms (their shoulder plates are the suit's own).
        public List<ThingDef> suits;
        // The arm's textures: <suit piece texPath>_<texKey>, e.g. Things/Pawn/PowerSuit/Bulwark/ArmL_minigun.
        public string texKey;
        // A gun arm: the pilot's weapon while they are in the suit.
        public ThingDef gun;
        // The gun when both arms carry this arm: one heavier burst.
        public ThingDef twinGun;
        // Melee attacks (HediffComp_VerbGiver) or stat changes (stages) given to the pilot.
        public HediffDef hediff;
        // When both arms carry this arm: textures drawn apart so the pair doesn't overlap.
        public string pairTexKey;
        // Drawn over the helmet facing south (a tower shield held up in front).
        public bool aboveHelmetSouth;
    }

    // On an arm gun: a weapon that exists only while a pilot is in a suit with that arm.
    public class ArmGunExtension : DefModExtension
    {
    }

    public static class SuitArmUtility
    {
        public static ArmModuleExtension Arm(ThingDef def) => def?.GetModExtension<ArmModuleExtension>();

        public static bool IsArmGun(Thing thing) => thing?.def.GetModExtension<ArmGunExtension>() != null;

        public static bool Fits(ThingDef arm, ThingDef suit)
        {
            var ext = Arm(arm);
            return ext?.suits != null && ext.suits.Contains(suit);
        }

        public static bool FitsSlot(ThingDef arm, ArmSlot slot)
        {
            var ext = Arm(arm);
            return ext != null && ext.back == (slot == ArmSlot.Back);
        }

        public static PowerSuitExtension Suit(ThingDef suit) => suit?.GetModExtension<PowerSuitExtension>();

        // Every ability the pilot gets from the suit and what is fitted to it.
        public static IEnumerable<AbilityDef> Abilities(Apparel_PowerSuit suit)
        {
            var own = Suit(suit.def)?.abilities;
            if (own != null)
                foreach (AbilityDef a in own)
                    yield return a;
            foreach (ThingDef def in suit.FittedArms())
            {
                var list = Arm(def)?.abilities;
                if (list != null)
                    foreach (AbilityDef a in list)
                        yield return a;
            }
        }

        // Gives the pilot what the fitted arms do: their melee attacks and stat changes, and the
        // arm gun as their weapon (their own weapon is stowed in their inventory meanwhile).
        public static void Apply(Apparel_PowerSuit suit, Pawn pilot)
        {
            foreach (ThingDef def in suit.FittedArms())
            {
                var ext = Arm(def);
                if (ext?.hediff != null && Boosting(suit, ext))
                    pilot.health.AddHediff(ext.hediff);
            }
            if (pilot.abilities != null)
                foreach (AbilityDef a in Abilities(suit))
                    pilot.abilities.GainAbility(a);
            EquipArmGun(suit, pilot);
        }

        // Takes it all back when the pilot climbs out, and gives back their own weapon.
        public static void Remove(Apparel_PowerSuit suit, Pawn pilot)
        {
            foreach (ThingDef def in suit.FittedArms())
            {
                var ext = Arm(def);
                if (ext?.hediff == null)
                    continue;
                Hediff h;
                while ((h = pilot.health.hediffSet.GetFirstHediffOfDef(ext.hediff)) != null)
                    pilot.health.RemoveHediff(h);
            }
            if (pilot.abilities != null)
                foreach (AbilityDef a in Abilities(suit))
                    pilot.abilities.RemoveAbility(a);
            Hediff unpowered = pilot.health.hediffSet.GetFirstHediffOfDef(RPS_DefOf.RPS_SuitUnpowered);
            if (unpowered != null)
                pilot.health.RemoveHediff(unpowered);
            DestroyArmGun(pilot);
            suit.RestoreStowedWeapon(pilot);
        }

        // A module that boosts an arm does nothing without that arm fitted.
        public static bool Boosting(Apparel_PowerSuit suit, ArmModuleExtension ext)
        {
            if (ext.boostsArm == null)
                return true;
            return Arm(suit.ArmIn(ArmSlot.Left))?.texKey == ext.boostsArm || Arm(suit.ArmIn(ArmSlot.Right))?.texKey == ext.boostsArm;
        }

        public static ThingDef ArmGunFor(Apparel_PowerSuit suit)
        {
            var left = Arm(suit.ArmIn(ArmSlot.Left));
            var right = Arm(suit.ArmIn(ArmSlot.Right));
            ThingDef l = left?.gun, r = right?.gun;
            if (l != null && l == r)
                return left.twinGun ?? l;
            if (l != null && r != null)
                return suit.rightGunActive ? r : l;
            return l ?? r;
        }

        public static void EquipArmGun(Apparel_PowerSuit suit, Pawn pilot)
        {
            ThingDef gun = ArmGunFor(suit);
            if (gun == null || pilot.equipment == null)
                return;
            ThingWithComps current = pilot.equipment.Primary;
            if (current != null && !IsArmGun(current))
                suit.StowWeapon(pilot, current);
            else if (current != null)
                DestroyArmGun(pilot);
            pilot.equipment.AddEquipment((ThingWithComps)ThingMaker.MakeThing(gun));
        }

        public static void DestroyArmGun(Pawn pilot)
        {
            ThingWithComps current = pilot.equipment?.Primary;
            if (current == null || !IsArmGun(current))
                return;
            pilot.equipment.Remove(current);
            current.Destroy();
        }
    }
}
