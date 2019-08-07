# -*- coding: utf-8 -*-
# imports
import csv
import datetime
import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from unidecode import unidecode

# Globals
MonitoringLocationHorizontalCoordinateReferenceSystem = "NAD27"
DatasetNamePostFix = " - Community Based Monitoring Program"
ActivityMediaName = "Surface water"
ResultDetectionQuantitationLimitType = "Method Detection Level"

# headers from the Mackenzie Data Stream Template
headers = ['DatasetName', 'MonitoringLocationID', 'MonitoringLocationName', 'MonitoringLocationLatitude',
           'MonitoringLocationLongitude', 'MonitoringLocationHorizontalCoordinateReferenceSystem',
           'MonitoringLocationType', 'MonitoringLocationWaterbody', 'ActivityType', 'ActivityMediaName',
           'ActivityStartDate', 'ActivityStartTime', 'ActivityEndDate', 'ActivityEndTime', 'ActivityDepthHeightMeasure',
           'ActivityDepthHeightUnit', 'SampleCollectionEquipmentName', 'CharacteristicName', 'MethodSpeciation',
           'ResultSampleFraction', 'ResultValue', 'ResultUnit', 'ResultDetectionCondition',
           'ResultDetectionQuantitationLimitMeasure', 'ResultDetectionQuantitationLimitUnit',
           'ResultDetectionQuantitationLimitType', 'ResultStatusID', 'ResultComment', 'ResultAnalyticalMethodID',
           'ResultAnalyticalMethodContext', 'ResultAnalyticalMethodName', 'AnalysisStartDate', 'AnalysisStartTime',
           'AnalysisStartTimeZone', 'LaboratoryName', 'LaboratorySampleID']

flaggedResult = "Below Detection/Quantification Limit"
now = datetime.datetime.now()
failedLocn = ''
failedChem = ''
error=0

# output files creation
f = open("LOG.txt", "w")  # logger
outFile = "MDS_DATA_" + str(now.day) + "-" + str(now.month) + "-" + str(now.year) + ".csv"  # output csv

# Lookup Tables
chemDict = {}  # chem lookup
reader = csv.DictReader(open("chemLookup.csv"))
for row in reader:
    chemDict[row["name"]] = row

locationDict = {}  # location lookup
reader = csv.DictReader(open("locationLookup.csv"))
for row in reader:
    locationDict[row["site_name"]] = row

tempDict = {}
for key in locationDict:
    nkey = key.lower()
    tempDict[nkey] = locationDict[key]
locationDict=tempDict


master = Tk()
Label(master, text="Data Type:").grid(row=0, sticky=W)
lab = IntVar()
Checkbutton(master, text="Lab", variable=lab).grid(row=1, sticky=W)
probe = IntVar()
Checkbutton(master, text="Probe", variable=probe).grid(row=2, sticky=W)
Button(master, text='Submit', command=master.quit).grid(row=3, sticky=W, pady=4)
mainloop()

# get the file to get transformed
if lab.get():
    fn = askopenfilename(title = "Lab Data")

    with open(fn, "r", encoding='UTF-8') as temp:
        x = open("temp.csv", "w")
        for row in temp:
            row = row.replace("µ", "u")  # removes the special characters
            x.writelines(unidecode(row))
    x.close()
    #-----------------------------------------------------------------------

    # the mapping transformation
    with open("temp.csv", newline='', encoding='UTF-8') as infile:
        with open(outFile, 'w', newline='') as csvfile:
            fieldnames = headers
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            incsv = csv.DictReader(infile)
            for inrow in incsv:

                #logging errors
                if not inrow['Client Sample ID'].lower() in locationDict.keys():
                    if not inrow['Client Sample ID'] in failedLocn:
                        failedLocn = failedLocn + inrow['Client Sample ID'] + ", "
                        error+=1
                    if not inrow['Parameter Name'] in chemDict.keys():
                        if not inrow['Parameter Name'] in failedChem:
                            failedChem = failedChem + inrow['Parameter Name'] + ", "
                            error += 1
                elif not inrow['Parameter Name'] in chemDict.keys():
                    if not inrow['Parameter Name'] in failedChem:
                        failedChem = failedChem + inrow['Parameter Name'] + ", "
                        error += 1
                elif not inrow['Reported Result']:
                    error+=0


                    #writing the good data
                else:
                    rowDictionary = dict.fromkeys(headers, "")
                    rowDictionary['DatasetName'] = inrow['Client Name'] + DatasetNamePostFix
                    rowDictionary['MonitoringLocationName'] = inrow['Client Sample ID']
                    rowDictionary[
                        'MonitoringLocationHorizontalCoordinateReferenceSystem'] = MonitoringLocationHorizontalCoordinateReferenceSystem
                    rowDictionary['ActivityMediaName'] = ActivityMediaName
                    rowDictionary['ActivityStartDate'] = inrow['Sample Collect Date']

                    if inrow['Result Flag'] != "":
                        rowDictionary["ResultDetectionCondition"] = flaggedResult
                    else:
                        if 'Final Result' in inrow.keys():
                            rowDictionary['ResultValue'] = inrow['Final Result']
                        else:
                            rowDictionary['ResultValue'] = inrow['Reported Result']

                        if inrow['Units'] == 'pH units':
                            inrow['Units'] = "None"
                        rowDictionary['ResultUnit'] = inrow['Units']


                    if inrow['CALC_MDL'] != '':
                        rowDictionary['ResultDetectionQuantitationLimitType'] = ResultDetectionQuantitationLimitType
                        rowDictionary['ResultDetectionQuantitationLimitUnit'] = inrow['Units']
                        rowDictionary['ResultDetectionQuantitationLimitMeasure'] = inrow['CALC_MDL']

                    if inrow['Client Sample ID'].casefold() in locationDict:
                        rowDictionary['MonitoringLocationLatitude'] = locationDict[inrow['Client Sample ID'].lower()]['lat']
                        rowDictionary['MonitoringLocationLongitude'] = locationDict[inrow['Client Sample ID'].lower()][
                            'long']
                        rowDictionary['MonitoringLocationType'] = locationDict[inrow['Client Sample ID'].lower()][
                            'MonitoringLocationType']
                        rowDictionary['MonitoringLocationWaterbody'] = locationDict[inrow['Client Sample ID'].lower()][
                            'MonitoringLocationWaterbody']

                    if inrow['Parameter Name'] in chemDict:
                        rowDictionary['ActivityType'] = chemDict[inrow['Parameter Name']]['ActivityType']
                        rowDictionary['SampleCollectionEquipmentName'] = chemDict[inrow['Parameter Name']][
                            'SampleCollectionEquipmentName']
                        rowDictionary['CharacteristicName'] = chemDict[inrow['Parameter Name']]['CharacteristicName']
                        rowDictionary['MethodSpeciation'] = chemDict[inrow['Parameter Name']]['MethodSpeciation']
                        rowDictionary['ResultSampleFraction'] = chemDict[inrow['Parameter Name']]['ResultSampleFraction']
                        rowDictionary['ResultComment'] = chemDict[inrow['Parameter Name']]['ResultComment']
                    writer.writerow(rowDictionary)


if probe.get():
    fn = askopenfilename(title="Probe Data")
    with open(fn, "r", encoding='UTF-8') as temp:
        x = open("temp.csv", "w")
        for row in temp:
            row = row.replace("µ", "u")  # removes the special characters
            x.writelines(unidecode(row))
    x.close()
    # -----------------------------------------------------------------------

    # the mapping transformation
    with open("temp.csv", newline='', encoding='UTF-8') as infile:
        with open(outFile, 'a+', newline='') as csvfile:
            fieldnames = headers
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            incsv = csv.DictReader(infile)
            for inrow in incsv:

                # logging errors
                if not inrow['#intro.site_name'].lower() in locationDict.keys():
                    if not inrow['#intro.site_name'] in failedLocn:
                        failedLocn = failedLocn + inrow['#intro.site_name'] + ", "
                        error += 1
                    if not inrow['parameter name'] in chemDict.keys():
                        if not inrow['parameter name'] in failedChem:
                            failedChem = failedChem + inrow['parameter name'] + ", "
                            error += 1
                elif not inrow['parameter name'] in chemDict.keys():
                    if not inrow['parameter name'] in failedChem:
                        failedChem = failedChem + inrow['parameter name'] + ", "
                        error += 1
                elif not inrow['Final result']:
                    error += 0

                    # writing the good data
                else:
                    rowDictionary = dict.fromkeys(headers, "")
                    rowDictionary['DatasetName'] = inrow['Client Name'] + DatasetNamePostFix
                    rowDictionary['MonitoringLocationName'] = inrow['#intro.site_name']
                    rowDictionary[
                        'MonitoringLocationHorizontalCoordinateReferenceSystem'] = MonitoringLocationHorizontalCoordinateReferenceSystem
                    rowDictionary['ActivityMediaName'] = ActivityMediaName
                    rowDictionary['ActivityStartDate'] = inrow['Date']


                    if 'Final result' in inrow.keys():
                        rowDictionary['ResultValue'] = inrow['Final result']
                    else:
                        rowDictionary['ResultValue'] = inrow['Reported Result']

                    rowDictionary['ResultUnit'] = chemDict[inrow['parameter name']]['Units']

                    '''
                    if inrow['CALC_MDL'] != '':
                        rowDictionary['ResultDetectionQuantitationLimitType'] = ResultDetectionQuantitationLimitType
                        rowDictionary['ResultDetectionQuantitationLimitUnit'] = inrow['Units']
                        rowDictionary['ResultDetectionQuantitationLimitMeasure'] = inrow['CALC_MDL']'''

                    if inrow['#intro.site_name'].casefold() in locationDict:
                        rowDictionary['MonitoringLocationLatitude'] = locationDict[inrow['#intro.site_name'].lower()][
                            'lat']
                        rowDictionary['MonitoringLocationLongitude'] = locationDict[inrow['#intro.site_name'].lower()][
                            'long']
                        rowDictionary['MonitoringLocationType'] = locationDict[inrow['#intro.site_name'].lower()][
                            'MonitoringLocationType']
                        rowDictionary['MonitoringLocationWaterbody'] = locationDict[inrow['#intro.site_name'].lower()][
                            'MonitoringLocationWaterbody']

                    if inrow['parameter name'] in chemDict:
                        rowDictionary['ActivityType'] = chemDict[inrow['parameter name']]['ActivityType']
                        rowDictionary['SampleCollectionEquipmentName'] = chemDict[inrow['parameter name']][
                            'SampleCollectionEquipmentName']
                        rowDictionary['CharacteristicName'] = chemDict[inrow['parameter name']]['CharacteristicName']
                        rowDictionary['MethodSpeciation'] = chemDict[inrow['parameter name']]['MethodSpeciation']
                        rowDictionary['ResultSampleFraction'] = chemDict[inrow['parameter name']][
                            'ResultSampleFraction']
                        rowDictionary['ResultComment'] = chemDict[inrow['parameter name']]['ResultComment']
                    writer.writerow(rowDictionary)

if error==0:
    f.write("NO Errors")
else:
    f.write("Failed Locations: " + failedLocn + "\nFailed Characteristic: " + failedChem)

os.remove("temp.csv")
