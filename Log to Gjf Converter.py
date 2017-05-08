import os
import re

#Ask for User Input
dictQ = {"1":"(1)Log directory?",
         "2":"(2)Destintation directory? If none, enter \"new\".",
         "3":"(3)Compatability? \"0\"-Sharcnet %nosave or \"1\"-Sharcnet.",
         "4":"(4)Basis set? 1/PM6 2/HF 3/B3LYPOPT 4/B3LYPFREQ 5/MP2",
         "5":"(5)Modify filename ending? Enter an ending string to remove. If none, write \"none\".",
         "6":"(6)GJF filename ending?",
         "7":"(7)Username?"}
'''"4":"(4)Memory? (No units)",
         "5":"(5)Number of processors?",
         "6":"(6)Basis set? 1/PM6 2/HF 3/B3LYPOPT 4/B3LYPFREQ 5/MP2",
         "7":"(7)Modify filename ending? Enter an ending string to remove. If none, write \"none\".",
         "8":"(8)GJF filename ending?",
         "9":"(9)Username?"}'''
dictI = {4:"2500",
         5:"4"} #Save User Input in Dict

i = 1    
print(dictQ[str(i)])
initialLogDir=input()
while os.path.isdir(initialLogDir) == False: 
    print("This directory could not be found. Enter again.")
    initialLogDir = input()
dictI.setdefault(i,initialLogDir)

i += 1 #2
print(dictQ[str(i)])
initialGjfDir = input()
if initialGjfDir == "new":
    print("Enter new directory title.")
    initialGjfDir2 = input()
    print("Up one level or stay in directory? If up one level, enter \"cd\". If stay in directory, press Enter.")
    gjfDirLocation = input()
    if gjfDirLocation == "cd":
        try:
            index = int(initialLogDir[len(initialLogDir):0:-1].index(chr(92)))*-1
            initialLogDir2 = initialLogDir[:index]
            os.chdir(initialLogDir2)
            os.mkdir(initialGjfDir2)
        except FileExistsError: print("This directory already exists. Your GJF files will be produced here.")
        dictI.setdefault(i,initialLogDir[:index]+initialGjfDir2)
    else:
        try: os.mkdir(initialLogDir+chr(92)+initialGjfDir2)
        except FileExistsError: print("This directory already exists. Your GJF files will be produced here.")
        dictI.setdefault(i,initialLogDir+chr(92)+initialGjfDir2)
else:
    while os.path.isdir(initialGjfDir) == False: 
        print("This directory could not be found. Enter again.")
        initialGjfDir = input()
    dictI.setdefault(i,initialGjfDir)
    
i += 1 #3
print(dictQ[str(i)])
inputComp = input()
while inputComp != "0" and inputComp != "1":  
    print("Enter \"0\" or \"1\".")
    inputComp = input()
dictI.setdefault(i,inputComp)

#Ask the rest in dictQ
while i < len(dictQ):
    i += 1
    print(dictQ[str(i)])
    if i == 4: 
        methodOption = input()
        if methodOption=="1": dictI.setdefault(i+2,"# opt pm6")
        elif methodOption=="2": dictI.setdefault(i+2,"# opt HF/3-21g")
        elif methodOption=="3": dictI.setdefault(i+2,"# opt b3lyp/6-311++g(d,p)")
        elif methodOption=="4": dictI.setdefault(i+2,"# freq b3lyp/6-311++g(d,p)")
        elif methodOption=="5": dictI.setdefault(i+2,"# mp2(full)/6-311++g(d,p)")
        else: dictI.setdefault(i+2,input())
    else:
        dictI.setdefault(i+2,input())
    while True:
        if not dictI[i+2]:
            print("Please enter an input."+dictQ[str(i)])
            dictI.setdefault(i+2,input())
        else: break
#Submission
while True: 
    print("Submit? Enter \"submit\". See a mistake? Enter \"fix\".")
    answer = input()
    while answer != "submit" and answer != "fix":  
        print("Enter \"submit\" or \"fix\".")
        answer = input()
    if answer == "fix":
        print("Enter the line number you wish to return to.")
        i = input()
        while i in dictI == False:
            print("This is not a valid line number. Try again.")
            i = input()
        print(dictQ[str(i)])
        dictI[int(i)] = input()
    else: break
logdirectory = dictI[1]
gjfdirectory = dictI[2]
inputComp = dictI[3]
inputMem = dictI[4]
inputProc = dictI[5]
inputBasis = dictI[6]
inputDel = dictI[7]
inputEnding = dictI[8]
username = dictI[9]

#Make list of log files in directory
listLogFiles = os.listdir(logdirectory) 
orgListLogFiles = [] #File names
i = 0
while i < len(listLogFiles):
    if ".log" not in listLogFiles[i][-4:]:
        listLogFiles.remove(listLogFiles[i])
    else: 
        orgListLogFiles.append(listLogFiles[i])
        listLogFiles.insert(i, logdirectory+"\\"+listLogFiles[i]) #listLogFiles = directory+file_name
        del listLogFiles[i+1]
        i += 1
    
#Define function to convert atomic number to symbol
def symbol(coordinate):
    periodicTable = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg', 
                       'Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','v','Cr','Mn', 
                       'Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr', 
                       'Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb', 
                       'Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd', 
                       'Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir', 
                       'Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac', 
                       'Th','Pa','U']
    return periodicTable[int(coordinate)-1]

listError = [["l9999/l103"],["l502"],["PBS"],["Other"]] #Set UP ErrorList
for i in range(len(orgListLogFiles)):
    #Read and extract data from listLogFiles[i]
    geom = []
    os.chdir(logdirectory)
    openLogFile = open(orgListLogFiles[i],"r")
    logFileString = openLogFile.read()
    
    #Write to Error List
    if "l9999" in logFileString or "l103" in logFileString: listError[0].append(orgListLogFiles[i])
    elif "l502" in logFileString: listError[1].append(orgListLogfiles[i])
    elif "PBS" in logFileString: listError[2].append(orgListLogFiles[i])
    elif "Normal termination" not in logFileString: listError[3].append(orgListLogFiles[i])

    #Make Resubmit"#" Directory for Failed Jobs in Log Directory
    if len(listError[0])==2 or len(listError[1])==2 or len(listError[2])==2:
        logDirectoryList = os.listdir(logdirectory)
        resubmitNumber = []
        for k in range(len(logDirectoryList)):
            if "Resubmit" in logDirectoryList[k] == True: resubmitNumber.append(logDirectoryList[k][9:])
        if resubmitNumber == []: resubmit = "\Resubmit_1"
        else: resubmit = "\Resubmit_"+str(int(max(resubmitNumber))+1)
        titleNumber = "_"+resubmit[len(resubmit)]
        if "Resubmit" in logdirectory: mainLogDirectory = logdirectory[:logdirectory.index("Resubmit")-1] #cd ..
        else: mainLogDirectory = logdirectory
        os.makedirs(mainLogdirectory+resubmit)
    
    #Write to geom list
    standardOri = re.findall(r"Standard orientation:(.*?)Rotational",logFileString,re.DOTALL) #edit
    lines = standardOri[len(standardOri)-1].split("\n") #list of lines in second last Standard Orientation table
    for j in range(len(lines)):
        if j>4 and j<(len(lines)-2):
            coordinates = lines[j].split() #list of (split lines)==list
            geom.append(symbol(coordinates[1])+" "*8+coordinates[3]+" "*4+coordinates[4]+" "*5+coordinates[5])

    #Prepare gjf lines
    if i == 0 and inputDel != "none":
        for j in range(len(orgListLogFiles)):
            while inputDel not in orgListLogFiles[j]:
                print(inputDel+" is not a substring for all files. Enter a new  filename ending to remove.")
                inputDel = input()
    if inputDel == "none": index = len(orgListLogFiles[i])-4
    else: index = int(orgListLogFiles[i].index(inputDel))
    title = orgListLogFiles[i][:index]+inputEnding+"\n\n"
    if orgListLogFiles[i] in listError[0] or orgListLogFiles[i] in listError[1] or orgListLogFiles[i] in listError[2]:
        title = orgListLogFiles[i][:index]+inputEnding+titleNumber
    if inputComp == "0": compatability = "%nosave\n"
    elif inputComp == "1": compatability = "%scr=/scratch/"+username+"/scr/"+orgListLogFiles[i][:index]+inputEnding+".scr\n"+"%rwf=/scratch/"+username+"/rwf/"+orgListLogFiles[i][:index]+inputEnding+".rwf\n"+"%chk=/scratch/"+username+"/chk/"+orgListLogFiles[i][:index]+inputEnding+".chk\n"
    memory = "%mem="+inputMem+"MB\n"
    proc = "%NProc="+inputProc+"\n"
    basisSet = inputBasis+"\n\n"
    if orgListLogFiles[i] in listError[1] and "int=(grid=ultrafine)" not in logFileString:
        basisSet = inputBasis+" int=(grid=ultrafine)\n\n"
    #elif orgListLOgFiles[i] in listError[1] and "int=(grid=ultrafine)" in logFileString:  
    if "-" in logFileString[logFileString.index("Charge")+9]:
        a = int(logFileString.index("Charge"))
        chargeLine = logFileString[a+9:a+11]+" "+logFileString[logFileString.index("Multiplicity")+15] +"\n"
    else: chargeLine = logFileString[logFileString.index("Charge")+10]+" "+logFileString[logFileString.index("Multiplicity")+15] +"\n"
    openLogFile.close()

    
    #Write gjf file
    if orgListLogFiles[i] not in listError[0] and orgListLogFiles[i] not in listError[1] and orgListLogFiles[i] not in listError[2]: openGjfFile = open(gjfdirectory+"\\"+orgListLogFiles[i][:index]+inputEnding+".gjf","w")
    elif orgListLogFiles[i] not in listError[3]: openGjfFile = open(logdirectory+resubmit+"\\"+orgListLogFiles[i]+".gjf","w")
    openGjfFile.write(compatability+memory+proc+basisSet+title+chargeLine)
    for j in range(len(geom)): openGjfFile.writelines(geom[j]+"\n")
    openGjfFile.writelines("\n\n\n")
    openGjfFile.close()
    
#Print Error List in Columns
os.chdir(gjfdirectory)
length = [[],[],[],[]]
printError = []
if len(listError[0])!=1 or len(listError[1])!=1 or len(listError[2])!=1 or len(listError[3])!=0:
    writeList = open("ErrorList.txt", "w")
    #Determine column width
    for i in range(len(listError)):
        for j in range(len(listError[i])): length[i].append(len(listError[i][j]))
    width = max(max(length[0]),max(length[1]),max(length[2]))+5
    #Make number of rows the same, Make list of lines to print, Print lines
    numberofRows = max(len(listError[0]),len(listError[1]),len(listError[2]),len(listError[3]))
    for i in range(len(listError)):
                       while len(listError[i]) != numberofRows: listError[i].append(" ")
    for i in range(numberofRows): printError.append([j[i] for j in listError])
    for j in printError: writeList.write(j[0]+" "*(width-len(j[0]))+j[1]+" "*(width-len(j[1]))+j[2]+" "*(width-len(j[2]))+j[3]+"\n")
    writeList.close()

print("Done")

#ASK JOSH RESUME, WHY "USE FAILED JOBS", HOW TO ACCCESS SERVER
#  C:\Users\McMahon Lab 002\Documents\Jihye\Brain\5-Fluorouracil\Solvenation\2 Water\1. PM6
#  C:\Users\McMahon Lab 002\Documents\Jihye\Brain\5-Fluorouracil\Solvenation\2 Water\Test HF
    
