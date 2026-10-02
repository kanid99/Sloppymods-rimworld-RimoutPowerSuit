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
