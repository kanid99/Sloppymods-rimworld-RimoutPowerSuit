using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimoutPowerSuit
{
    [StaticConstructorOnStartup]
    public static class RimoutPowerSuitMod
    {
        public static readonly Texture2D ExitSuitIcon = ContentFinder<Texture2D>.Get("UI/Commands/RPS_ExitPowerSuit");

        static RimoutPowerSuitMod()
        {
            new Harmony("sloppymod.rimoutpowersuit").PatchAll();
        }
    }

    [DefOf]
    public static class RPS_DefOf
    {
        public static JobDef RPS_EnterPowerSuit;
        public static JobDef RPS_ExitPowerSuit;

        static RPS_DefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RPS_DefOf));
        }
    }
}
