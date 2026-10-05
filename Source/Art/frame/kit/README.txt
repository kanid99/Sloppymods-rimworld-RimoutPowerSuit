POWER ARMOUR FRAME - layer kit (concept art, not yet in the mod)

Every file is 320 x 320 px on the suit's canvas: drawSize (2.717, 2.717), the pawn's position at the
centre (160,160), the same as the suit textures in Textures/Things/Pawn/PowerSuit/. West = east mirrored.
Redraw any layer in place (same size, same position) and it drops straight in.

Draw order, back to front (the pilot's body and head are the game's own pawn, drawn 26 px higher than
normal so the head clears the collar - see Pilot_reference_*.png):

SOUTH   Hatch_south_stageN  ->  Frame_back_south  ->  pilot  ->  Frame_front_south
        (while the pilot walks up behind the frame, they go first, under the raised hatch; once inside only
         what rises above y = 112 shows, so the head comes up through the collar)
EAST    Frame_back_east  ->  pilot  ->  Hatch_east_stageN  ->  Frame_front_east
NORTH   Frame_back_north  ->  pilot body  ->  Frame_front_north  ->  pilot head  ->  Collar_front_north
        ->  Hinges_north (only while shut; once the hatch moves they go under it)  ->  Hatch_north_stageN
        (while the pilot walks up from behind, they are drawn last, over everything)

Hatch stages: 0 = shut, 5 = fully open (135 degrees), evenly spaced. In game the climb-in plays
open 0->5, pilot steps in, close 5->0.
GUIDE.png shows every layer with the pawn position, head, collar and feet lines and the tile grid.
