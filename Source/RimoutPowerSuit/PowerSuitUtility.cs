using RimWorld;
using Verse;

namespace RimoutPowerSuit
{
    public static class PowerSuitUtility
    {
        // Set only while a pilot is climbing out: the Unlock patch refuses to unlock a suit otherwise.
        public static bool AllowUnlock;

        public static int ClimbTicks(Apparel_PowerSuit suit) =>
            UnityEngine.Mathf.Max(60, suit.GetStatValue(StatDefOf.EquipDelay).SecondsToTicks());

        public static Apparel_PowerSuit WornSuit(Pawn pawn)
        {
            if (pawn?.apparel == null)
                return null;
            var worn = pawn.apparel.WornApparel;
            for (int i = 0; i < worn.Count; i++)
            {
                if (worn[i] is Apparel_PowerSuit suit)
                    return suit;
            }
            return null;
        }

        // Why this pawn cannot climb into this suit, or null if they can.
        public static string CannotEnterReason(Pawn pawn, Apparel_PowerSuit suit)
        {
            if (pawn.apparel == null || !pawn.RaceProps.Humanlike)
                return "RPS.CannotEnterNotHumanlike".Translate(pawn.LabelShort);
            if (!pawn.DevelopmentalStage.Adult())
                return "RPS.CannotEnterNotAdult".Translate(pawn.LabelShort);
            if (WornSuit(pawn) != null)
                return "RPS.CannotEnterAlreadyPiloting".Translate(pawn.LabelShort);
            if (!ApparelUtility.HasPartsToWear(pawn, suit.def))
                return "CannotWearBecauseOfMissingBodyParts".Translate();
            if (!EquipmentUtility.CanEquip(suit, pawn, out string reason))
                return reason;
            if (pawn.apparel.WouldReplaceLockedApparel(suit))
                return "WouldReplaceLockedApparel".Translate().CapitalizeFirst();
            return null;
        }

        // Puts the pilot in: anything they wear that the suit encloses (outer armour, headgear)
        // is dropped at their feet.
        public static void PutIn(Pawn pawn, Apparel_PowerSuit suit)
        {
            if (suit.Spawned)
                suit.DeSpawn();
            pawn.apparel.Wear(suit, dropReplacedApparel: true, locked: true);
            SuitArmUtility.Apply(suit, pawn);
        }

        // Takes the pilot out and stands the empty suit where they were. The arms stop working
        // (the arm gun goes, the pilot's own weapon comes back); a weapon that only a suited
        // pilot can hold - the warcasket guns - is dropped with the suit.
        public static void TakeOut(Pawn pawn, Apparel_PowerSuit suit)
        {
            SuitArmUtility.Remove(suit, pawn);
            AllowUnlock = true;
            try
            {
                pawn.apparel.Unlock(suit);
            }
            finally
            {
                AllowUnlock = false;
            }

            if (!pawn.apparel.TryDrop(suit, out _, pawn.PositionHeld, false))
            {
                Log.Error("[Rimout Power Suit] Could not drop " + suit + " from " + pawn + ".");
                pawn.apparel.Lock(suit);
                return;
            }

            ThingWithComps weapon = pawn.equipment?.Primary;
            if (weapon != null && !EquipmentUtility.CanEquip(weapon, pawn))
                pawn.equipment.TryDropEquipment(weapon, out _, pawn.PositionHeld, false);
        }
    }
}
