using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimoutPowerSuit
{
    // A power suit: apparel locked onto its pilot while worn, and a standing suit on the ground
    // when nobody is inside. Climbing in and out are jobs (JobDriver_EnterPowerSuit and
    // JobDriver_ExitPowerSuit); nothing else may take it off.
    public class Apparel_PowerSuit : Apparel
    {
        public override IEnumerable<Gizmo> GetWornGizmos()
        {
            foreach (Gizmo gizmo in base.GetWornGizmos())
                yield return gizmo;

            Pawn pilot = Wearer;
            if (pilot == null || !pilot.IsColonistPlayerControlled)
                yield break;

            var exit = new Command_Action
            {
                defaultLabel = "RPS.ExitSuit".Translate(),
                defaultDesc = "RPS.ExitSuitDesc".Translate(LabelNoParenthesisCap),
                icon = RimoutPowerSuitMod.ExitSuitIcon,
                action = () => pilot.jobs.TryTakeOrderedJob(JobMaker.MakeJob(RPS_DefOf.RPS_ExitPowerSuit, pilot), JobTag.Misc)
            };
            if (pilot.Downed)
                exit.Disable("RPS.PilotDowned".Translate(pilot.LabelShort));
            yield return exit;
        }
    }
}
