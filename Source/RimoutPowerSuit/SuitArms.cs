using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimoutPowerSuit
{
    public enum ArmSlot
    {
        Left,
        Right
    }

    // On an arm module item: what fitting it to a suit does.
    public class ArmModuleExtension : DefModExtension
    {
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

        // Gives the pilot what the fitted arms do: their melee attacks and stat changes, and the
        // arm gun as their weapon (their own weapon is stowed in their inventory meanwhile).
        public static void Apply(Apparel_PowerSuit suit, Pawn pilot)
        {
            foreach (ThingDef def in suit.FittedArms())
            {
                var ext = Arm(def);
                if (ext?.hediff != null)
                    pilot.health.AddHediff(ext.hediff);
            }
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
            DestroyArmGun(pilot);
            suit.RestoreStowedWeapon(pilot);
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
