
Make sure your file is saved as a CSV file in UTF-8 format. This can be done in excel.

If your file is an CSV and it still does not work, you may need make sure it is saved in UTF-8 format.

[How to make the CSV UTF-8 file](https://help.evertrue.com/article/347-creating-a-utf-8-encoded-csv-file)

## RUN:
Navigate to the MDS folder then into dist folder then click the Transformer app
Select the file you want to convert
The output will be in the MDS_Chem_DD-MM-YYYY.csv
log file will hold any locations or chemical tests that were not determined.

### ADD NEW LOCATIONS:
open MDS folder then dist folder open the locationLookup file and add the new location there
the file is structured as:
site_name	lat		long		MonitoringLocationType	MonitoringLocationWaterbody
snowbirds	58.35669029	-111.5469713	River/Stream		Athbasca River

### ADD NEW CHEMICAL TEST:
open MDS folder then dist folder open the chemLookup file and add the new chemical test there

name(in the lab report,Required) ActivityType(in MDS,Required)	SampleCollectionEquipmentName(in MDS,Required)	CharacteristicName(in MDS,Required)	MethodSpeciation(in MDS, Optional)	ResultSampleFraction(in MDS, Optional)	ResultComment(in MDS,Optional)
Nitrate as Nitrogen		 Sample-Routine			Water Bottle					Nitrate					as N					Total

### Required File Dependencies
chemLookup.csv has the specific info for each chemical we test for.

locationLookup.csv has the specific info for each location surveyed.

#### Example Input Files
Lab_Data.csv is an example of the lab file it accepts to be transformed
Probe_Data.csv is an example of the lab file it accepts to be transformed
The program will run and output a transformed csv which can be submitted to the DataStream as well as a log that notifies of any locations or chemicals it could not map appropriately 
If there was a location or chemical in the log those will not be included in the output and you should update the lookup files. Delete the old output file and rerun the program.

#### Example Output files
csv will be output as MDS_DATA_DD-MM-YYYY (MDS_DATA_7-8-2019)

## to make executable application
executable that exists should work for Windows this should only be required if you change the source code or are building it on mac

you will need Python 3

navigate into the Make directory and run
'pip install -r requirements.txt'

Navigate into the same directory as the transformer.py file and run
'pyinstaller transformer.py --onefile'

move the chemLookup.csv and locationLookup.csv into the dist directory next to the application
