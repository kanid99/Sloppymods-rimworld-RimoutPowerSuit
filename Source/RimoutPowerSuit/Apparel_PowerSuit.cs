using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimoutPowerSuit
{
    // A power suit: apparel locked onto its pilot while worn, and a standing suit on the ground
    // when nobody is inside. Climbing in and out are jobs (JobDriver_EnterPowerSuit and
    // JobDriver_ExitPowerSuit); nothing else may take it off. Arms are fitted to the standing
    // suit (JobDriver_FitSuitArm) and work while a pilot is inside (SuitArmUtility).
    public class Apparel_PowerSuit : Apparel
    {
        private ThingDef armLeft;
        private ThingDef armRight;
        // With two different gun arms: which one the pilot is firing.
        public bool rightGunActive;
        // The pilot's own weapon, stowed in their inventory while an arm gun is their weapon.
        private ThingWithComps stowedWeapon;

        public ThingDef ArmIn(ArmSlot slot) => slot == ArmSlot.Left ? armLeft : armRight;

        public IEnumerable<ThingDef> FittedArms()
        {
            if (armLeft != null)
                yield return armLeft;
            if (armRight != null)
                yield return armRight;
        }

        // Fits an arm (null = bare). Returns the arm that was there, if any.
        public ThingDef SetArm(ArmSlot slot, ThingDef arm)
        {
            ThingDef old = ArmIn(slot);
            if (slot == ArmSlot.Left)
                armLeft = arm;
            else
                armRight = arm;
            return old;
        }

        public void StowWeapon(Pawn pilot, ThingWithComps weapon)
        {
            pilot.equipment.Remove(weapon);
            if (pilot.inventory != null && pilot.inventory.innerContainer.TryAdd(weapon))
                stowedWeapon = weapon;
            else
                GenPlace.TryPlaceThing(weapon, pilot.PositionHeld, pilot.MapHeld, ThingPlaceMode.Near);
        }

        public void RestoreStowedWeapon(Pawn pilot)
        {
            ThingWithComps weapon = stowedWeapon;
            stowedWeapon = null;
            if (weapon == null || pilot.inventory == null || !pilot.inventory.innerContainer.Contains(weapon))
                return;
            pilot.inventory.innerContainer.Remove(weapon);
            if (pilot.equipment != null && pilot.equipment.Primary == null)
                pilot.equipment.AddEquipment(weapon);
            else if (pilot.MapHeld != null)
                GenPlace.TryPlaceThing(weapon, pilot.PositionHeld, pilot.MapHeld, ThingPlaceMode.Near);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref armLeft, "armLeft");
            Scribe_Defs.Look(ref armRight, "armRight");
            Scribe_Values.Look(ref rightGunActive, "rightGunActive");
            Scribe_References.Look(ref stowedWeapon, "stowedWeapon");
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string arms = "RPS.ArmsInspect".Translate(
                armLeft != null ? armLeft.LabelCap.Resolve() : "RPS.ArmBare".Translate().Resolve(),
                armRight != null ? armRight.LabelCap.Resolve() : "RPS.ArmBare".Translate().Resolve());
            return s.NullOrEmpty() ? arms : s + "\n" + arms;
        }

        // The standing suit is drawn from the same piece textures as the worn one, facing south,
        // so its fitted arms show.
        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            var nodes = def.apparel?.RenderNodeProperties;
            if (nodes == null || nodes.Count == 0)
            {
                base.DrawAt(drawLoc, flip);
                return;
            }
            int i = 0;
            foreach (PawnRenderNodeProperties props in nodes.OrderBy(SouthLayer))
            {
                string path = PawnRenderNode_SuitPiece.TexPathFor(props, this);
                Graphic g = GraphicDatabase.Get<Graphic_Multi>(path, ShaderDatabase.CutoutComplex, props.drawSize, DrawColor);
                g.Draw(drawLoc + new Vector3(0f, 0.002f * i++, 0f), Rot4.South, this);
            }
            Comps_PostDraw();
        }

        // The piece's layer facing south; an arm held up in front (a tower shield) goes over the helmet.
        private float SouthLayer(PawnRenderNodeProperties p)
        {
            float layer = p.drawData != null ? p.drawData.LayerForRot(Rot4.South, p.baseLayer) : p.baseLayer;
            if (p is PawnRenderNodeProperties_SuitPiece piece && piece.isArm && SuitArmUtility.Arm(ArmIn(piece.slot))?.aboveHelmetSouth == true)
                layer += 4f;
            return layer;
        }

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

            // Two different gun arms: switch which one fires.
            ThingDef left = SuitArmUtility.Arm(armLeft)?.gun, right = SuitArmUtility.Arm(armRight)?.gun;
            if (left != null && right != null && left != right)
            {
                ThingDef other = rightGunActive ? armLeft : armRight;
                yield return new Command_Action
                {
                    defaultLabel = "RPS.SwitchArm".Translate(other.LabelCap),
                    defaultDesc = "RPS.SwitchArmDesc".Translate(),
                    icon = other.uiIcon,
                    action = () =>
                    {
                        rightGunActive = !rightGunActive;
                        SuitArmUtility.EquipArmGun(this, pilot);
                    }
                };
            }
        }
    }
}
