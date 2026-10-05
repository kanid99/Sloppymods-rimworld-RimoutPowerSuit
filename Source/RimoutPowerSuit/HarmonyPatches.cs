using HarmonyLib;
using RimWorld;
using Verse;

namespace RimoutPowerSuit
{
    // A suit is only ever taken off by climbing out: nothing else - the gear tab, an
    // ideoligion role change, low hit points - may unlock it.
    [HarmonyPatch(typeof(Pawn_ApparelTracker), nameof(Pawn_ApparelTracker.Unlock))]
    public static class Pawn_ApparelTracker_Unlock_Patch
    {
        public static bool Prefix(Apparel apparel) =>
            !(apparel is Apparel_PowerSuit) || PowerSuitUtility.AllowUnlock;
    }

    // The suit encloses its pilot: it cannot be worn with outer armour or headgear. It has a
    // layer of its own, so vanilla would otherwise let them stack.
    [HarmonyPatch(typeof(ApparelUtility), nameof(ApparelUtility.CanWearTogether))]
    public static class ApparelUtility_CanWearTogether_Patch
    {
        public static void Postfix(ThingDef A, ThingDef B, ref bool __result)
        {
            if (!__result || A == B)
                return;
            if ((IsSuit(A) && Enclosed(B)) || (IsSuit(B) && Enclosed(A)))
                __result = false;
        }

        private static bool IsSuit(ThingDef def) =>
            def?.thingClass != null && typeof(Apparel_PowerSuit).IsAssignableFrom(def.thingClass);

        private static bool Enclosed(ThingDef def)
        {
            if (def?.apparel?.layers == null)
                return false;
            if (IsSuit(def))
                return true;
            foreach (ApparelLayerDef layer in def.apparel.layers)
            {
                if (layer == ApparelLayerDefOf.Shell || layer == ApparelLayerDefOf.Overhead
                    || layer == ApparelLayerDefOf.EyeCover)
                    return true;
            }
            return false;
        }
    }

    // Colonists never climb into a suit on their own: outfit optimisation scores suits out.
    [HarmonyPatch(typeof(JobGiver_OptimizeApparel), nameof(JobGiver_OptimizeApparel.ApparelScoreRaw))]
    public static class JobGiver_OptimizeApparel_ApparelScoreRaw_Patch
    {
        public static void Postfix(Apparel ap, ref float __result)
        {
            if (ap is Apparel_PowerSuit)
                __result = -1000f;
        }
    }

    // Right-clicking a suit offers "Climb into", not vanilla's "Wear".
    [HarmonyPatch(typeof(FloatMenuOptionProvider_Wear), "GetSingleOptionFor", typeof(Thing), typeof(FloatMenuContext))]
    public static class FloatMenuOptionProvider_Wear_Patch
    {
        public static bool Prefix(Thing clickedThing, ref FloatMenuOption __result)
        {
            if (clickedThing is Apparel_PowerSuit)
            {
                __result = null;
                return false;
            }
            return true;
        }
    }

    // An arm gun is part of the suit: it is never dropped (not when downed, stripped or killed);
    // it is removed in code when the pilot climbs out.
    [HarmonyPatch(typeof(Pawn_EquipmentTracker), nameof(Pawn_EquipmentTracker.TryDropEquipment))]
    public static class Pawn_EquipmentTracker_TryDropEquipment_Patch
    {
        public static bool Prefix(ThingWithComps eq, ref ThingWithComps resultingEq, ref bool __result)
        {
            if (!SuitArmUtility.IsArmGun(eq))
                return true;
            resultingEq = null;
            __result = false;
            return false;
        }
    }

    // A pilot whose suit arm is their weapon can't pick up or equip another weapon.
    [HarmonyPatch(typeof(EquipmentUtility), nameof(EquipmentUtility.CanEquip),
        new[] { typeof(Thing), typeof(Pawn), typeof(string), typeof(bool) },
        new[] { ArgumentType.Normal, ArgumentType.Normal, ArgumentType.Out, ArgumentType.Normal })]
    public static class EquipmentUtility_CanEquip_Patch
    {
        public static void Postfix(Thing thing, Pawn pawn, ref string cantReason, ref bool __result)
        {
            if (!__result || thing == null || !thing.def.IsWeapon || SuitArmUtility.IsArmGun(thing))
                return;
            if (SuitArmUtility.IsArmGun(pawn?.equipment?.Primary))
            {
                cantReason = "RPS.ArmGunFitted".Translate();
                __result = false;
            }
        }
    }
}
