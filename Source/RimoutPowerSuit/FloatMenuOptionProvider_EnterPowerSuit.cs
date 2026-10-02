using RimWorld;
using Verse;
using Verse.AI;

namespace RimoutPowerSuit
{
    // Right-click a standing suit: "Climb into ...". The class existing is registration enough -
    // the game collects every FloatMenuOptionProvider subclass. Vanilla's "Wear" option is
    // removed for suits by a patch (HarmonyPatches.cs).
    public class FloatMenuOptionProvider_EnterPowerSuit : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!(clickedThing is Apparel_PowerSuit suit) || !suit.Spawned)
                return null;

            Pawn pawn = context.FirstSelectedPawn;
            string label = "RPS.EnterSuit".Translate(suit.LabelShort);

            string reason = PowerSuitUtility.CannotEnterReason(pawn, suit);
            if (reason == null && !pawn.CanReach(suit, PathEndMode.Touch, Danger.Deadly))
                reason = "NoPath".Translate().CapitalizeFirst();
            if (reason == null && !pawn.CanReserve(suit))
            {
                Pawn other = pawn.Map.reservationManager.FirstRespectedReserver(suit, pawn);
                reason = other != null
                    ? "ReservedBy".Translate(other.LabelShort, other).Resolve()
                    : "Reserved".Translate().Resolve();
            }
            if (reason != null)
                return new FloatMenuOption(label + ": " + reason, null);

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, () =>
            {
                suit.SetForbidden(false, false);
                pawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(RPS_DefOf.RPS_EnterPowerSuit, suit), JobTag.Misc);
            }, MenuOptionPriority.High), pawn, suit);
        }
    }
}
