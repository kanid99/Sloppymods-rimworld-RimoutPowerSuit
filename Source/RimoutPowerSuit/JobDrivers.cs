using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimoutPowerSuit
{
    // TargetA: the standing suit.
    public class JobDriver_EnterPowerSuit : JobDriver
    {
        private Apparel_PowerSuit Suit => (Apparel_PowerSuit)job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOnBurningImmobile(TargetIndex.A);
            this.FailOn(() => PowerSuitUtility.CannotEnterReason(pawn, Suit) != null);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(PowerSuitUtility.ClimbTicks(Suit), TargetIndex.A)
                .WithProgressBarToilDelay(TargetIndex.A)
                .FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_General.Do(() => PowerSuitUtility.PutIn(pawn, Suit));
        }
    }

    // TargetA: the pilot.
    public class JobDriver_ExitPowerSuit : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => PowerSuitUtility.WornSuit(pawn) == null);

            Apparel_PowerSuit suit = PowerSuitUtility.WornSuit(pawn);
            int ticks = suit != null ? PowerSuitUtility.ClimbTicks(suit) : 60;
            yield return Toils_General.Wait(ticks)
                .WithProgressBarToilDelay(TargetIndex.A);
            yield return Toils_General.Do(() =>
            {
                Apparel_PowerSuit worn = PowerSuitUtility.WornSuit(pawn);
                if (worn != null)
                    PowerSuitUtility.TakeOut(pawn, worn);
            });
        }
    }
}

namespace RimoutPowerSuit
{
    // TargetA: the standing suit; TargetB: the arm module item; TargetC: the slot, as a cell
    // whose x is the ArmSlot (job.count is the carry amount, so it can't hold the slot).
    // Carries the arm to the suit and fits it; an arm already in that slot comes off as an item.
    public static class SuitArmJobs
    {
        public static Job Make(JobDef def, Thing suit, Thing arm, ArmSlot slot)
        {
            Job job = arm != null ? JobMaker.MakeJob(def, suit, arm, new IntVec3((int)slot, 0, 0))
                                  : JobMaker.MakeJob(def, suit, LocalTargetInfo.Invalid, new IntVec3((int)slot, 0, 0));
            job.count = 1;
            return job;
        }

        public static ArmSlot Slot(Job job) => (ArmSlot)job.GetTarget(TargetIndex.C).Cell.x;
    }

    public class JobDriver_FitSuitArm : JobDriver
    {
        public const int FitTicks = 300;

        private Apparel_PowerSuit Suit => (Apparel_PowerSuit)job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed)
            && pawn.Reserve(job.GetTarget(TargetIndex.B), job, 1, 1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !SuitArmUtility.Fits(job.GetTarget(TargetIndex.B).Thing?.def, Suit.def));
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.B);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(FitTicks, TargetIndex.A)
                .WithProgressBarToilDelay(TargetIndex.A)
                .FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_General.Do(() =>
            {
                Thing arm = pawn.carryTracker.CarriedThing;
                if (arm == null)
                    return;
                Apparel_PowerSuit suit = Suit;
                ThingDef old = suit.SetArm(SuitArmJobs.Slot(job), arm.def);
                pawn.carryTracker.DestroyCarriedThing();
                if (old != null)
                    GenPlace.TryPlaceThing(ThingMaker.MakeThing(old), suit.Position, suit.Map, ThingPlaceMode.Near);
            });
        }
    }

    // TargetA: the standing suit; TargetC: the slot (see JobDriver_FitSuitArm). Takes the arm off as an item.
    public class JobDriver_RemoveSuitArm : JobDriver
    {
        private Apparel_PowerSuit Suit => (Apparel_PowerSuit)job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Suit.ArmIn(SuitArmJobs.Slot(job)) == null);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(JobDriver_FitSuitArm.FitTicks / 2, TargetIndex.A)
                .WithProgressBarToilDelay(TargetIndex.A);
            yield return Toils_General.Do(() =>
            {
                Apparel_PowerSuit suit = Suit;
                ThingDef old = suit.SetArm(SuitArmJobs.Slot(job), null);
                if (old != null)
                    GenPlace.TryPlaceThing(ThingMaker.MakeThing(old), suit.Position, suit.Map, ThingPlaceMode.Near);
            });
        }
    }
}
