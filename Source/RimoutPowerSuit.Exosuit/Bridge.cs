using System.Collections.Generic;
using Exosuit;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

// Exosuit mode: compiled against Exosuit Framework (Aoba.Exosuit.Framework) and loaded only
// when it is active (LoadFolders.xml -> Mods/Exosuit). The framework parks a suit on a
// maintenance bay and gets pilots in and out there; these classes let our suit stand
// anywhere instead. A one-tile "suit stand" bay appears under a pilot who climbs out, and
// vanishes once someone climbs back in. Everything else - modules, repair at real bays,
// structure points - is the framework's.
namespace RimoutPowerSuit.ExosuitBridge
{
    [DefOf]
    public static class BridgeDefOf
    {
        public static ThingDef RPS_SuitStand;
        public static JobDef RPS_DeploySuit;
        public static JobDef RPS_ClimbOutToStand;

        static BridgeDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(BridgeDefOf));
    }

    [StaticConstructorOnStartup]
    public static class BridgeTextures
    {
        public static readonly Texture2D ClimbOut = ContentFinder<Texture2D>.Get("UI/Commands/RPS_ExitPowerSuit");
    }

    public static class SuitStandUtility
    {
        // Why a suit cannot be left standing on this cell, or null if it can.
        public static string CannotStandAt(IntVec3 cell, Map map)
        {
            if (map == null || !cell.InBounds(map) || !cell.Standable(map))
                return "RPS.NoRoomForSuit".Translate();
            if (cell.GetEdifice(map) != null)
                return "RPS.NoRoomForSuit".Translate();
            return null;
        }

        public static Building_SuitStand SpawnStand(IntVec3 cell, Map map, Faction faction, Rot4 rot)
        {
            var stand = (Building_SuitStand)ThingMaker.MakeThing(BridgeDefOf.RPS_SuitStand);
            stand.SetFactionDirect(faction);
            GenSpawn.Spawn(stand, cell, map, rot);
            return stand;
        }
    }

    // A maintenance bay with no equipment: just where a suit stands while nobody is in it.
    // Not buildable; it exists only while it holds a suit.
    public class Building_SuitStand : Building_MaintenanceBay
    {
        protected override void Tick()
        {
            base.Tick();
            if (!Spawned)
                return;
            TryUpdateCache();
            if (!HasGearCore)
                Destroy(DestroyMode.Vanish);
        }
    }

    // The suit's core, as worn: adds "Climb out here", which leaves the suit standing where
    // the pilot is instead of needing a bay.
    public class PowerSuitCore : Exosuit_Core
    {
        public override IEnumerable<Gizmo> GetWornGizmos()
        {
            foreach (Gizmo g in base.GetWornGizmos())
                yield return g;

            Pawn pilot = Wearer;
            if (pilot == null || !pilot.IsColonistPlayerControlled || !pilot.Spawned)
                yield break;
            if (Extesnsion != null && !Extesnsion.CanGearOff)
                yield break;

            var climbOut = new Command_Action
            {
                defaultLabel = "RPS.ClimbOutHere".Translate(),
                defaultDesc = "RPS.ClimbOutHereDesc".Translate(),
                icon = BridgeTextures.ClimbOut,
                action = () => pilot.jobs.TryTakeOrderedJob(JobMaker.MakeJob(BridgeDefOf.RPS_ClimbOutToStand, pilot), JobTag.Misc)
            };
            string reason = SuitStandUtility.CannotStandAt(pilot.Position, pilot.Map);
            if (pilot.Downed)
                reason = "RPS.PilotDowned".Translate(pilot.LabelShort);
            if (reason != null)
                climbOut.Disable(reason);
            yield return climbOut;
        }
    }

    // TargetA: the pilot. Climbs out and leaves the suit standing on their cell, facing the
    // way they faced.
    public class JobDriver_ClimbOutToStand : JobDriver
    {
        private const int Ticks = 240;

        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => !pawn.PawnWearingExosuitCore());
            yield return Toils_General.Wait(Ticks).WithProgressBarToilDelay(TargetIndex.A);
            yield return Toils_General.Do(() =>
            {
                string reason = SuitStandUtility.CannotStandAt(pawn.Position, pawn.Map);
                if (reason != null)
                {
                    Messages.Message(reason, pawn, MessageTypeDefOf.RejectInput, false);
                    return;
                }
                // The framework draws the parked suit facing away from the stand's rotation.
                var stand = SuitStandUtility.SpawnStand(pawn.Position, pawn.Map, pawn.Faction, pawn.Rotation.Opposite);
                stand.GearDown(pawn);
            });
        }
    }

    // TargetA: a crafted suit core lying on the ground. Stands it up where it lies, ready to
    // be climbed into.
    public class JobDriver_DeploySuit : JobDriver
    {
        private const int Ticks = 180;

        private Thing Core => job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(Ticks, TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A)
                .FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_General.Do(() =>
            {
                Thing core = Core;
                string reason = SuitStandUtility.CannotStandAt(core.Position, core.Map);
                if (reason != null)
                {
                    Messages.Message(reason, core, MessageTypeDefOf.RejectInput, false);
                    return;
                }
                var stand = SuitStandUtility.SpawnStand(core.Position, core.Map, pawn.Faction, Rot4.North);
                stand.AddOrReplaceModule(core);
            });
        }
    }

    // Right-click a suit core lying on the ground: "Set up ... here".
    public class FloatMenuOptionProvider_DeploySuit : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (clickedThing == null || !clickedThing.Spawned || clickedThing.def.GetModExtension<DeployableCoreExtension>() == null)
                return null;
            Pawn pawn = context.FirstSelectedPawn;
            string label = "RPS.DeploySuit".Translate(clickedThing.LabelShort);
            string reason = SuitStandUtility.CannotStandAt(clickedThing.Position, clickedThing.Map);
            if (reason == null && !pawn.CanReserveAndReach(clickedThing, PathEndMode.Touch, Danger.Deadly))
                reason = "NoPath".Translate().CapitalizeFirst();
            if (reason != null)
                return new FloatMenuOption(label + ": " + reason, null);
            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, () =>
                pawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(BridgeDefOf.RPS_DeploySuit, clickedThing), JobTag.Misc)), pawn, clickedThing);
        }
    }

    // Marks a core item that can be stood up anywhere with "Set up ... here".
    public class DeployableCoreExtension : DefModExtension
    {
    }
}
