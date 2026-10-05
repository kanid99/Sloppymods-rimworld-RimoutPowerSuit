using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

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
        private ThingDef backpack;
        // Power, counted in cells (1 = one full cell). -1 until set (new suits start full).
        private float charge = -1f;
        // Net launcher ammunition.
        public int nets = -1;
        // The backpack's shield generator: on/off, its energy (damage it can still absorb) and
        // when the pilot last moved (it comes up after standing still).
        public bool shieldEnabled = true;
        private float shieldEnergy;
        private int lastMovedTick;

        public const float ShieldMaxEnergy = 220f;
        public const int ShieldStillTicks = 60;
        // Cells per day the shield draws while up, and per point of damage it absorbs.
        public const float ShieldDrainPerDay = 1f;
        public const float ShieldDrainPerDamage = 0.002f;
        // With two different gun arms: which one the pilot is firing.
        public bool rightGunActive;
        // The pilot's own weapon, stowed in their inventory while an arm gun is their weapon.
        private ThingWithComps stowedWeapon;

        public ThingDef ArmIn(ArmSlot slot) => slot == ArmSlot.Left ? armLeft : slot == ArmSlot.Right ? armRight : backpack;

        // Arms and backpack.
        public IEnumerable<ThingDef> FittedArms()
        {
            if (armLeft != null)
                yield return armLeft;
            if (armRight != null)
                yield return armRight;
            if (backpack != null)
                yield return backpack;
        }

        // Fits an arm or backpack (null = none). Returns what was there, if anything.
        public ThingDef SetArm(ArmSlot slot, ThingDef arm)
        {
            ThingDef old = ArmIn(slot);
            if (slot == ArmSlot.Left)
                armLeft = arm;
            else if (slot == ArmSlot.Right)
                armRight = arm;
            else
                backpack = arm;
            charge = Mathf.Min(Charge, Capacity);
            return old;
        }

        // ---------------------------------------------------------------- power

        public PowerSuitExtension SuitExt => SuitArmUtility.Suit(def);

        // Cells: the backpack's if it has its own, else the suit's.
        public int Cells
        {
            get
            {
                int pack = SuitArmUtility.Arm(backpack)?.cells ?? 0;
                return pack > 0 ? pack : SuitExt?.cells ?? 1;
            }
        }

        public float Capacity => Cells;

        public float Charge => charge < 0f ? Capacity : charge;

        public bool Powered => Charge > 0f;

        public int MaxNets => SuitExt?.nets ?? 0;

        public int Nets => nets < 0 ? MaxNets : nets;

        public void Drain(float cells) => charge = Mathf.Max(0f, Charge - cells);

        public void Recharge(float cells) => charge = Mathf.Min(Capacity, Charge + cells);

        public void AddNets(int n) => nets = Mathf.Clamp(Nets + n, 0, MaxNets);

        public bool HasShield => SuitArmUtility.Arm(backpack)?.shield == true;

        public bool ShieldUp
        {
            get
            {
                Pawn pilot = Wearer;
                return HasShield && shieldEnabled && Powered && pilot != null && pilot.Spawned && !pilot.Downed
                       && Find.TickManager.TicksGame - lastMovedTick >= ShieldStillTicks;
            }
        }

        public override void PostMake()
        {
            base.PostMake();
            charge = Capacity;
            nets = MaxNets;
        }

        // Called while worn (HarmonyPatches: the apparel tracker's interval tick).
        public void SuitTickInterval(Pawn pilot, int delta)
        {
            if (pilot.pather != null && pilot.pather.MovingNow)
                lastMovedTick = Find.TickManager.TicksGame;
            float drain = (SuitExt?.drainPerDay ?? 0.5f) * delta / GenDate.TicksPerDay;
            var pack = SuitArmUtility.Arm(backpack);
            if (pack?.workJob != null && pilot.CurJobDef == pack.workJob && SuitArmUtility.Boosting(this, pack))
                drain += pack.workDrainPerDay * delta / GenDate.TicksPerDay;
            if (ShieldUp)
            {
                drain += ShieldDrainPerDay * delta / GenDate.TicksPerDay;
                shieldEnergy = Mathf.Min(ShieldMaxEnergy, shieldEnergy + ShieldMaxEnergy * delta / 600f);
            }
            Drain(drain);
            // an empty suit's servos stop: the pilot can barely move it
            Hediff unpowered = pilot.health.hediffSet.GetFirstHediffOfDef(RPS_DefOf.RPS_SuitUnpowered);
            if (!Powered && unpowered == null)
                pilot.health.AddHediff(RPS_DefOf.RPS_SuitUnpowered);
            else if (Powered && unpowered != null)
                pilot.health.RemoveHediff(unpowered);
        }

        // The shield absorbs every kind of damage while it is up; the pilot can still fire out.
        public override bool CheckPreAbsorbDamage(DamageInfo dinfo)
        {
            Pawn pilot = Wearer;
            if (!ShieldUp || shieldEnergy <= 0f || !dinfo.Def.harmsHealth || pilot == null)
                return base.CheckPreAbsorbDamage(dinfo);
            shieldEnergy -= dinfo.Amount;
            Drain(dinfo.Amount * ShieldDrainPerDamage);
            SoundDefOf.EnergyShield_AbsorbDamage.PlayOneShot(new TargetInfo(pilot.Position, pilot.Map));
            FleckMaker.Static(pilot.TrueCenter(), pilot.Map, FleckDefOf.ExplosionFlash, 4f);
            if (shieldEnergy <= 0f)
            {
                shieldEnergy = 0f;
                EffecterDefOf.Shield_Break.SpawnAttached(pilot, pilot.MapHeld, 1.6f);
            }
            return true;
        }

        public override void DrawWornExtras()
        {
            base.DrawWornExtras();
            Pawn pilot = Wearer;
            if (pilot == null || !ShieldUp || shieldEnergy <= 0f)
                return;
            float size = Mathf.Lerp(2.4f, 2.9f, shieldEnergy / ShieldMaxEnergy);
            Vector3 pos = pilot.DrawPos;
            pos.y = AltitudeLayer.MoteOverhead.AltitudeFor();
            Matrix4x4 matrix = Matrix4x4.TRS(pos, Quaternion.AngleAxis(Rand.Range(0f, 360f), Vector3.up), new Vector3(size, 1f, size));
            Graphics.DrawMesh(MeshPool.plane10, matrix, SuitTextures.ShieldBubble, 0);
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
            Scribe_Defs.Look(ref backpack, "backpack");
            Scribe_Values.Look(ref charge, "charge", -1f);
            Scribe_Values.Look(ref nets, "nets", -1);
            Scribe_Values.Look(ref shieldEnabled, "shieldEnabled", true);
            Scribe_Values.Look(ref shieldEnergy, "shieldEnergy");
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string arms = "RPS.ArmsInspect".Translate(
                armLeft != null ? armLeft.LabelCap.Resolve() : "RPS.ArmBare".Translate().Resolve(),
                armRight != null ? armRight.LabelCap.Resolve() : "RPS.ArmBare".Translate().Resolve());
            arms += "\n" + "RPS.PowerInspect".Translate((Charge / Capacity).ToStringPercent(), Cells);
            if (backpack != null)
                arms += "\n" + "RPS.BackpackInspect".Translate(backpack.LabelCap.Resolve());
            if (MaxNets > 0)
                arms += "\n" + "RPS.NetsInspect".Translate(Nets, MaxNets);
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

            yield return new Gizmo_SuitPower(this);
            if (HasShield)
            {
                yield return new Command_Toggle
                {
                    defaultLabel = "RPS.ShieldToggle".Translate(),
                    defaultDesc = "RPS.ShieldToggleDesc".Translate(),
                    icon = SuitTextures.ShieldIcon,
                    isActive = () => shieldEnabled,
                    toggleAction = () => shieldEnabled = !shieldEnabled
                };
            }

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
