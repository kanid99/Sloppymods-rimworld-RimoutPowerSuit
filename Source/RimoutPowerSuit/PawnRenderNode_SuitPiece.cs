using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimoutPowerSuit
{
    // One piece of a worn suit (body, legs, an arm, the helmet), drawn as its own render node so
    // each piece can later be damaged and drawn on its own. The suit lists its pieces in
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

        private Color SuitColor(Pawn pawn)
        {
            Apparel suit = apparel ?? PowerSuitUtility.WornSuit(pawn);
            return suit != null ? suit.DrawColor : Color.white;
        }

        public override GraphicMeshSet MeshSetFor(Pawn pawn) =>
            MeshPool.GetMeshSetForSize(props.drawSize.x, props.drawSize.y);

        public override Color ColorFor(Pawn pawn) => SuitColor(pawn);

        public override Graphic GraphicFor(Pawn pawn) =>
            GraphicDatabase.Get<Graphic_Multi>(props.texPath, ShaderDatabase.CutoutComplex, props.drawSize, SuitColor(pawn));

        protected override IEnumerable<Graphic> GraphicsFor(Pawn pawn)
        {
            yield return GraphicFor(pawn);
        }
    }

    // Draws a suit piece whenever clothes are drawn. Position and layer come from the node's
    // drawData; the piece is not scaled by body type (one suit fits every pilot).
    public class PawnRenderNodeWorker_SuitPiece : PawnRenderNodeWorker
    {
        public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms) =>
            base.CanDrawNow(node, parms) && parms.flags.FlagSet(PawnRenderFlags.Clothes);
    }
}
