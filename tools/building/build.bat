@echo off
cd ..

pyinstaller adjust_FL_midi.py --onefile --clean ^
--icon ".\building\Icons\FL hat.ico" ^
--name "Adjust FL Midi" ^
--distpath ".\building\built" ^
--workpath ".\building\working"


pyinstaller overlap_detector.py --onefile --clean ^
--icon ".\building\Icons\triangle.ico" ^
--name "Overlap Detector" ^
--distpath ".\building\built" ^
--workpath ".\building\working"


pyinstaller read_midi_file.py --onefile --clean ^
--icon ".\building\Icons\bongo.ico" ^
--name "Read Midi File" ^
--distpath ".\building\built" ^
--workpath ".\building\working"


pyinstaller change_expression_to_volume.py --onefile --clean ^
--icon ".\building\Icons\guitar.ico" ^
--name "Change Expression To Volume" ^
--distpath ".\building\built" ^
--workpath ".\building\working"



pyinstaller fix_patch_events.py --onefile --clean ^
--icon ".\building\Icons\trombone.ico" ^
--name "Fix Patch Events" ^
--distpath ".\building\built" ^
--workpath ".\building\working"