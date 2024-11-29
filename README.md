# SpaceEngineers Blueprint Calculator 
### **It works with mods! It supports custom inputs! It requires VSCode!** *And even more if you wish to write your own code...*
<br/><br/>
<br/><br/>
## How it works:
This is a simple batch of scripts which does string matching and calculation. The input data it requires are: your game folder, your mod folder, your blueprint save folder. All the processed data is stored as separate configuration files next to the script itself. You can use the file sctructure which scripts use for your benefit by modifying the .xml files however you want. The examples folder is there to help you figure out how to write entries yourself.
1. Run **eaBPCalculator_parsingPart.py** to create the Database file from user-specified game and mod folders. It will be called "parsedData.xml".
2. Run **eaBPCalculator_exportBPComps.py** next to export the components data from your bp.sbc. It will require the Database file in the location of script to do all the string matching. The result will be written to "exportComponents.xml".
3. Run **eaBPCalculator_exportBPMats.py** after that to get the information on the required resources/materials/ingots(however you call them) from the "exportComponents.xml" using the Database file. The result will be written to "exportMaterials.xml".
