using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using UnityEngine;
using Verse.AI;

namespace RimoutPowerSuit
{
    // Right-click a standing suit: "Fit <arm> (left arm)" for the nearest arm module or backpack of
    // each kind on the map that fits this suit, "Take off <arm> (left arm)" for fitted ones, and
    // "Load nets" for a suit with a net launcher.
    public class FloatMenuOptionProvider_SuitArms : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        private static readonly ArmSlot[] Slots = { ArmSlot.Left, ArmSlot.Right, ArmSlot.Back };

        private static string SlotLabel(ArmSlot slot) =>
            (slot == ArmSlot.Left ? "RPS.LeftArm" : slot == ArmSlot.Right ? "RPS.RightArm" : "RPS.BackSlot").Translate();

        public override IEnumerable<FloatMenuOption> GetOptionsFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!(clickedThing is Apparel_PowerSuit suit) || !suit.Spawned)
                yield break;
            Pawn pawn = context.FirstSelectedPawn;
            if (!pawn.CanReach(suit, PathEndMode.Touch, Danger.Deadly))
                yield break;

            foreach (ArmSlot slot in Slots)
            {
                string slotLabel = SlotLabel(slot);
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

            // the net launcher: 20 textiles per net
            if (suit.MaxNets > 0 && suit.Nets < suit.MaxNets)
            {
                int want = (suit.MaxNets - suit.Nets) * JobDriver_ReloadSuitNets.PerNet;
                Thing cloth = GenClosest.ClosestThingReachable(suit.Position, suit.Map, ThingRequest.ForGroup(ThingRequestGroup.HaulableEver),
                    PathEndMode.ClosestTouch, TraverseParms.For(pawn), 9999f,
                    t => t.def.IsStuff && t.def.stuffProps.categories != null && t.def.stuffProps.categories.Contains(StuffCategoryDefOf.Fabric)
                         && t.stackCount >= JobDriver_ReloadSuitNets.PerNet && !t.IsForbidden(pawn) && pawn.CanReserve(t));
                string label = "RPS.LoadNets".Translate(suit.Nets, suit.MaxNets);
                if (cloth == null)
                    yield return new FloatMenuOption(label + ": " + "RPS.NoTextiles".Translate(JobDriver_ReloadSuitNets.PerNet), null);
                else
                {
                    int count = Mathf.Min(cloth.stackCount, want) / JobDriver_ReloadSuitNets.PerNet * JobDriver_ReloadSuitNets.PerNet;
                    yield return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, () =>
                    {
                        Job job = JobMaker.MakeJob(RPS_DefOf.RPS_ReloadSuitNets, suit, cloth);
                        job.count = count;
                        pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
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
                foreach (ArmSlot slot in Slots)
                {
                    if (suit.ArmIn(slot) == arm.def)
                        continue;
                    string slotLabel = SlotLabel(slot);
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
