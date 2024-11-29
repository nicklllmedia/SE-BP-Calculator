# SpaceEngineers Blueprint Calculator
For now all you have to know is:
* It is unfinished
* You need to run Python code yourself
<br/><br/>
<br/><br/>
<br/><br/>
## How it works(briefly):
1. Run **eaBPCalculator_parsingPart.py** to create the Database file. It will be called "parsedData.xml".
2. Run **eaBPCalculator_exportBPComps.py** next to export the components data from your bp.sbc. It will require the Database file in the location of script to do all the string matching. The result will be written to "exportComponents.xml".
3. Run **eaBPCalculator_exportBPMats.py** after that to get the information on the required resources/materials/ingots(however you call them) from the "exportComponents.xml" using the Database file. The result will be written to "exportMaterials.xml".
