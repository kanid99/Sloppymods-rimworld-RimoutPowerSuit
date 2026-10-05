using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimoutPowerSuit
{
    // A suit piece's render node properties. An arm piece draws the arm fitted to its slot; the
    // body piece draws the fitted backpack (it is part of the body's textures).
    public class PawnRenderNodeProperties_SuitPiece : PawnRenderNodeProperties
    {
        public bool isArm;
        public ArmSlot slot;
        public bool isBody;
    }

    // One piece of a worn suit (body, legs, an arm, the helmet), drawn as its own render node so
    // each piece can be fitted, damaged and drawn on its own. The suit lists its pieces in
    // apparel.renderNodeProperties: texPath (a Graphic_Multi with CutoutComplex masks, red =
    // the suit's colour), drawSize (the suit is bigger than the pawn's own body mesh) and a
    // layer per facing (drawData), since the pieces overlap differently from each side.
    public class PawnRenderNode_SuitPiece : PawnRenderNode_Apparel
    {
        public PawnRenderNode_SuitPiece(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
            : base(pawn, props, tree)
        {
        }

        public PawnRenderNode_SuitPiece(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree, Apparel apparel)
            : base(pawn, props, tree, apparel)
        {
        }

        public Apparel_PowerSuit Suit(Pawn pawn) => apparel as Apparel_PowerSuit ?? PowerSuitUtility.WornSuit(pawn);

        // An arm piece: <texPath>_<arm's texKey>, or the bare arm. Both arms carrying the same arm
        // with a pair texture (two tower shields) use that instead.
        public static string TexPathFor(PawnRenderNodeProperties props, Apparel_PowerSuit suit)
        {
            if (!(props is PawnRenderNodeProperties_SuitPiece piece) || suit == null)
                return props.texPath;
            if (piece.isBody)
            {
                string packKey = SuitArmUtility.Arm(suit.ArmIn(ArmSlot.Back))?.texKey;
                return packKey != null ? props.texPath + "_" + packKey : props.texPath;
            }
            if (!piece.isArm)
                return props.texPath;
            ThingDef arm = suit.ArmIn(piece.slot);
            var ext = SuitArmUtility.Arm(arm);
            if (ext?.texKey == null)
                return props.texPath;
            ThingDef other = suit.ArmIn(piece.slot == ArmSlot.Left ? ArmSlot.Right : ArmSlot.Left);
            string key = other == arm && ext.pairTexKey != null ? ext.pairTexKey : ext.texKey;
            return props.texPath + "_" + key;
        }

        private Color SuitColor(Pawn pawn)
        {
            Apparel suit = Suit(pawn);
            return suit != null ? suit.DrawColor : Color.white;
        }

        public override GraphicMeshSet MeshSetFor(Pawn pawn) =>
            MeshPool.GetMeshSetForSize(props.drawSize.x, props.drawSize.y);

        public override Color ColorFor(Pawn pawn) => SuitColor(pawn);

        public override Graphic GraphicFor(Pawn pawn) =>
            GraphicDatabase.Get<Graphic_Multi>(TexPathFor(props, Suit(pawn)), ShaderDatabase.CutoutComplex, props.drawSize, SuitColor(pawn));

        protected override IEnumerable<Graphic> GraphicsFor(Pawn pawn)
        {
            yield return GraphicFor(pawn);
        }
    }

    // Draws a suit piece whenever clothes are drawn, at the node's layer for the facing. An arm
    // held up in front (a tower shield) is drawn over the helmet facing south.
    public class PawnRenderNodeWorker_SuitPiece : PawnRenderNodeWorker
    {
        public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms) =>
            base.CanDrawNow(node, parms) && parms.flags.FlagSet(PawnRenderFlags.Clothes);

        public override float LayerFor(PawnRenderNode node, PawnDrawParms parms)
        {
            float layer = base.LayerFor(node, parms);
            if (parms.facing == Rot4.South && node.Props is PawnRenderNodeProperties_SuitPiece piece && piece.isArm
                && node is PawnRenderNode_SuitPiece n)
            {
                var ext = SuitArmUtility.Arm(n.Suit(parms.pawn)?.ArmIn(piece.slot));
                if (ext != null && ext.aboveHelmetSouth)
                    layer += 4f;
            }
            return layer;
        }
    }
}
