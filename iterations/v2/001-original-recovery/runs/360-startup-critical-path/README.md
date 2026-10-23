# Run360: startup path priorities

The real entry is host WinMain -> original004b6710 -> app_main004b6a50.
Linker names are not a countdown: they include conditional CD/duplicate-instance
paths and later splash/audio/frame references. Current Run102 link has no
WHOLEARCHIVE override. A linked EXE, a real display and a playable menu are
separate milestones; none is yet proven.

The next substantive original subsystem is unconditional00536e50 device setup
(456B) plus00563ad0 pool setup (251B), before render_startup00467470 and display
construction004677e0.361 owns source/native proof;362 collects their original
bodies and three unrecovered children in one REA session. Reuse accepted direct
children; no guessed DirectInput state or dummy service return.

Earlier startup gates still need exact providers: CD relaunch004a5c30 imports
and instance check005655f0, thread/lock/bootstrap bindings and partial005679f0.
Detailed order, addresses and boundaries are retained in evidence.json. Full
renderer/resource/frontend/game and visual validation remain open.
