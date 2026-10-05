using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimoutPowerSuit
{
    [StaticConstructorOnStartup]
    public static class SuitTextures
    {
        public static readonly Material ShieldBubble = MaterialPool.MatFrom("Other/ShieldBubble", ShaderDatabase.Transparent);
        public static readonly Texture2D ShieldIcon = ContentFinder<Texture2D>.Get("UI/Commands/RPS_SuitShield");
        public static readonly Texture2D BarFull = SolidColorMaterials.NewSolidColorTexture(new Color(0.95f, 0.75f, 0.2f));
        public static readonly Texture2D BarEmpty = SolidColorMaterials.NewSolidColorTexture(Color.clear);
    }

    // The worn suit's power, as a bar beside its buttons.
    public class Gizmo_SuitPower : Gizmo
    {
        private readonly Apparel_PowerSuit suit;

        public Gizmo_SuitPower(Apparel_PowerSuit suit)
        {
            this.suit = suit;
            Order = -100f;
        }

        public override float GetWidth(float maxWidth) => 140f;

        public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
        {
            Rect rect = new Rect(topLeft.x, topLeft.y, GetWidth(maxWidth), 75f);
            Rect inner = rect.ContractedBy(6f);
            Widgets.DrawWindowBackground(rect);
            Rect label = inner;
            label.height = rect.height / 2f;
            Text.Font = GameFont.Tiny;
            Widgets.Label(label, "RPS.PowerGizmo".Translate(suit.Cells));
            Rect bar = inner;
            bar.yMin = inner.y + inner.height / 2f;
            float pct = suit.Charge / suit.Capacity;
            Widgets.FillableBar(bar, pct, SuitTextures.BarFull, SuitTextures.BarEmpty, false);
            Text.Font = GameFont.Small;
            Text.Anchor = TextAnchor.MiddleCenter;
            Widgets.Label(bar, pct.ToStringPercent());
            Text.Anchor = TextAnchor.UpperLeft;
            TooltipHandler.TipRegion(rect, "RPS.PowerGizmoDesc".Translate());
            return new GizmoResult(GizmoState.Clear);
        }
    }

    // Drives a worn suit: power drain, the shield, running out of power.
    [HarmonyPatch(typeof(Pawn_ApparelTracker), nameof(Pawn_ApparelTracker.ApparelTrackerTickInterval))]
    public static class Pawn_ApparelTracker_TickInterval_Patch
    {
        public static void Postfix(Pawn_ApparelTracker __instance, int delta)
        {
            Pawn pawn = __instance.pawn;
            if (pawn == null || pawn.Dead)
                return;
            PowerSuitUtility.WornSuit(pawn)?.SuitTickInterval(pawn, delta);
        }
    }

    // A charging rack: while powered, recharges the cells of standing suits next to it.
    public class CompProperties_SuitCharger : CompProperties
    {
        public float cellsPerDay = 4f;
        public float radius = 1.9f;

        public CompProperties_SuitCharger() => compClass = typeof(CompSuitCharger);
    }

    public class CompSuitCharger : ThingComp
    {
        public CompProperties_SuitCharger Props => (CompProperties_SuitCharger)props;

        public override void CompTickRare()
        {
            base.CompTickRare();
            var power = parent.GetComp<CompPowerTrader>();
            if (power != null && !power.PowerOn)
                return;
            foreach (Apparel_PowerSuit suit in SuitsInReach())
                suit.Recharge(Props.cellsPerDay * GenTicks.TickRareInterval / GenDate.TicksPerDay);
        }

        public IEnumerable<Apparel_PowerSuit> SuitsInReach()
        {
            Map map = parent.Map;
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(parent.Position, Props.radius, true))
            {
                if (!cell.InBounds(map))
                    continue;
                List<Thing> things = cell.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                    if (things[i] is Apparel_PowerSuit suit)
                        yield return suit;
            }
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            GenDraw.DrawRadiusRing(parent.Position, Props.radius);
        }

        public override string CompInspectStringExtra()
        {
            int n = 0;
            foreach (Apparel_PowerSuit _ in SuitsInReach())
                n++;
            return "RPS.ChargerInspect".Translate(n);
        }
    }

    // ---------------------------------------------------------------- abilities

    // An ability powered by the suit: greyed out without enough charge. The cost is paid by
    // the verb (Verb_SuitJump) or by Apply.
    public class CompProperties_SuitPower : CompProperties_AbilityEffect
    {
        public float cells = 0.5f;
        public bool payOnApply = true;

        public CompProperties_SuitPower() => compClass = typeof(CompAbilityEffect_SuitPower);
    }

    public class CompAbilityEffect_SuitPower : CompAbilityEffect
    {
        public new CompProperties_SuitPower Props => (CompProperties_SuitPower)props;

        public override bool GizmoDisabled(out string reason)
        {
            var suit = PowerSuitUtility.WornSuit(parent.pawn);
            if (suit == null || suit.Charge < Props.cells)
            {
                reason = "RPS.NotEnoughPower".Translate(Props.cells.ToString("0.##"));
                return true;
            }
            return base.GizmoDisabled(out reason);
        }

        public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
        {
            base.Apply(target, dest);
            if (Props.payOnApply)
                PowerSuitUtility.WornSuit(parent.pawn)?.Drain(Props.cells);
        }
    }

    // The jump pack: a jump that drains the suit's cells.
    public class Verb_SuitJump : Verb_CastAbilityJump
    {
        protected override bool TryCastShot()
        {
            var suit = PowerSuitUtility.WornSuit(CasterPawn);
            var cost = ability?.CompOfType<CompAbilityEffect_SuitPower>()?.Props.cells ?? 0f;
            if (suit == null || suit.Charge < cost)
                return false;
            bool jumped = base.TryCastShot();
            if (jumped)
                suit.Drain(cost);
            return jumped;
        }
    }

    // The net launcher: needs a net loaded; firing uses one.
    public class CompProperties_SuitNets : CompProperties_AbilityEffect
    {
        public CompProperties_SuitNets() => compClass = typeof(CompAbilityEffect_SuitNets);
    }

    public class CompAbilityEffect_SuitNets : CompAbilityEffect
    {
        public override bool GizmoDisabled(out string reason)
        {
            var suit = PowerSuitUtility.WornSuit(parent.pawn);
            if (suit == null || suit.Nets <= 0)
            {
                reason = "RPS.NoNets".Translate();
                return true;
            }
            return base.GizmoDisabled(out reason);
        }

        public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
        {
            base.Apply(target, dest);
            PowerSuitUtility.WornSuit(parent.pawn)?.AddNets(-1);
        }
    }

    // A net: everything under it is slowed; insects are pinned.
    public class Projectile_Net : Projectile
    {
        public const float Radius = 2.4f;

        protected override void Impact(Thing hitThing, bool blockedByShield = false)
        {
            Map map = Map;
            IntVec3 center = Position;
            base.Impact(hitThing, blockedByShield);
            if (map == null)
                return;
            FleckMaker.Static(center, map, FleckDefOf.ExplosionFlash, 6f);
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(center, map, Radius, true))
            {
                if (!(t is Pawn p) || p.Dead)
                    continue;
                HediffDef def = p.RaceProps.Insect ? NetDefOf.RPS_NettedInsect : NetDefOf.RPS_Netted;
                Hediff old = p.health.hediffSet.GetFirstHediffOfDef(def);
                if (old != null)
                    p.health.RemoveHediff(old);
                p.health.AddHediff(def);
            }
        }
    }

    [DefOf]
    public static class NetDefOf
    {
        public static HediffDef RPS_Netted;
        public static HediffDef RPS_NettedInsect;

        static NetDefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(NetDefOf));
    }

    // TargetA: the standing suit; TargetB: textiles to load. Twenty textiles make a net.
    public class JobDriver_ReloadSuitNets : JobDriver
    {
        public const int PerNet = 20;

        private Apparel_PowerSuit Suit => (Apparel_PowerSuit)job.GetTarget(TargetIndex.A).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed)
            && pawn.Reserve(job.GetTarget(TargetIndex.B), job, 1, job.count, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Suit.Nets >= Suit.MaxNets);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(TargetIndex.B);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B, false, true);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(180, TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A);
            yield return Toils_General.Do(() =>
            {
                Thing cloth = pawn.carryTracker.CarriedThing;
                if (cloth == null)
                    return;
                Apparel_PowerSuit suit = Suit;
                int n = Mathf.Min(cloth.stackCount / PerNet, suit.MaxNets - suit.Nets);
                suit.AddNets(n);
                if (n * PerNet >= cloth.stackCount)
                    pawn.carryTracker.DestroyCarriedThing();
                else
                    cloth.stackCount -= n * PerNet;
            });
        }
    }
}
