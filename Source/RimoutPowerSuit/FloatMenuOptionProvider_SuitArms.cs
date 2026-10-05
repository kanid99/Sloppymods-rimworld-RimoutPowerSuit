using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimoutPowerSuit
{
    // Right-click a standing suit: "Fit <arm> (left arm)" for the nearest arm module of each kind
    // on the map that fits this suit, and "Take off <arm> (left arm)" for fitted arms.
    public class FloatMenuOptionProvider_SuitArms : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        public override IEnumerable<FloatMenuOption> GetOptionsFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!(clickedThing is Apparel_PowerSuit suit) || !suit.Spawned)
                yield break;
            Pawn pawn = context.FirstSelectedPawn;
            if (!pawn.CanReach(suit, PathEndMode.Touch, Danger.Deadly))
                yield break;

            foreach (ArmSlot slot in new[] { ArmSlot.Left, ArmSlot.Right })
            {
                string slotLabel = (slot == ArmSlot.Left ? "RPS.LeftArm" : "RPS.RightArm").Translate();
                ThingDef fitted = suit.ArmIn(slot);
                if (fitted != null)
                {
                    ArmSlot s = slot;
                    yield return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                        "RPS.RemoveArm".Translate(fitted.label, slotLabel), () =>
                        {
                            pawn.jobs.TryTakeOrderedJob(SuitArmJobs.Make(RPS_DefOf.RPS_RemoveSuitArm, suit, null, s), JobTag.Misc);
                        }), pawn, suit);
                }
            }

            // the nearest usable arm module of each kind that fits this suit
            var arms = suit.Map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver)
                .Where(t => SuitArmUtility.Fits(t.def, suit.def) && !t.IsForbidden(pawn)
                            && pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Deadly))
                .GroupBy(t => t.def)
                .Select(g => g.OrderBy(t => t.Position.DistanceToSquared(suit.Position)).First());
            foreach (Thing arm in arms)
            {
                foreach (ArmSlot slot in new[] { ArmSlot.Left, ArmSlot.Right })
                {
                    if (suit.ArmIn(slot) == arm.def)
                        continue;
                    string slotLabel = (slot == ArmSlot.Left ? "RPS.LeftArm" : "RPS.RightArm").Translate();
                    ArmSlot s = slot;
                    Thing a = arm;
                    yield return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                        "RPS.FitArm".Translate(arm.def.label, slotLabel), () =>
                        {
                            suit.SetForbidden(false, false);
                            pawn.jobs.TryTakeOrderedJob(SuitArmJobs.Make(RPS_DefOf.RPS_FitSuitArm, suit, a, s), JobTag.Misc);
                        }), pawn, suit);
                }
            }
        }
    }
}
