import re

class ExamScheduleInfo:

    ANYDAYEXCEPTION = "4:00-4:59"
    KEY_FOR_ANY = "Any"
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday"]

    def __init__(self, infoTxtFile=""):
        self.InfoTxtFile = infoTxtFile
        self.ExamDictionary = {}
        self.ClassToFinalDict = {}
        self.SpecialDays = []

    def fillDictionary(self):
        ignore = ["AM", "PM"]

        if self.InfoTxtFile == "":
            print("Text file containing exam schedule not set.")
        else:
            examFile = open(self.InfoTxtFile, "r")

            for line in examFile:
                lineSplit = line.split()
                if len(lineSplit) > 0 and re.match("[0-9]{1,2}:[0-9]{2}-[0-9]{1,2}:[0-9]{2}", lineSplit[0]):
                    weekDayKeys = [] #this is for MWF, WF, F, etc.
                    startTimeKey = 0
                    for string in lineSplit:
                        string = string.replace(',', "")
                        if string in ignore:
                            pass
                        elif string == lineSplit[0] and string != ExamScheduleInfo.ANYDAYEXCEPTION:
                            isAfternoon = lineSplit[1] == "PM"
                            key = self._createRangeForStartTime(string, isAfternoon)
                            startTimeKey = key

                            if key not in self.ExamDictionary:
                                self.ExamDictionary[key] = {}
                        elif string == ExamScheduleInfo.ANYDAYEXCEPTION:
                            scheduledTime = self._getExamScheduleForAnyDay(lineSplit)
                            key = self._createRangeForStartTime(string, True)
                            self.ExamDictionary[key] = {}
                            self.ExamDictionary[key][ExamScheduleInfo.KEY_FOR_ANY] = scheduledTime
                            break
                        elif string == "TBA":
                            for wdk in weekDayKeys:
                                self.ExamDictionary[startTimeKey][wdk] = string
                        elif string in ExamScheduleInfo.WEEKDAYS:
                            scheduledTime = " ".join(lineSplit[lineSplit.index(string):])
                            for wdk in weekDayKeys:
                                self.ExamDictionary[startTimeKey][wdk] = scheduledTime
                            break
                        elif '*' in string:
                            string = string.replace('*', "")
                            self.SpecialDays.append(string)
                            weekDayKeys.append(string)
                        else: #normal class days with no special cases
                            weekDayKeys.append(string)

    def parseClassSchedule(self, scheduleFileName):
        scheduleFile = open(scheduleFileName, "r")
        classToFinalDict = {}
        for line in scheduleFile:
            lineSplit = line.split()
            if len(lineSplit) == 0:
                pass
            elif lineSplit[0][0:2] == '//':
                pass
            else:
                try:
                    className = lineSplit[0]
                    startTime = int(lineSplit[1].replace(':', ""))
                    if lineSplit[2].upper() == "PM":
                        startTime += 1200
                    classDays = lineSplit[3].upper()
                    classToFinalDict[className] = self._getFinalForClassTimeAndDays(startTime, classDays)
                except Exception as e:
                    print("****************")
                    print("ALERT: Error parsing schedule for %s. Check formatting. (Press ENTER to continue)" % (className))
                    print("Error details:", e)
                    print("****************")
                    input()
        self.ClassToFinalDict = classToFinalDict

    def prettyPrintClassToFinalDate(self):
        anyIsSpecial = False
        ppFormatString = "%+15s   %+10s   %+15s"
        ppFormatStringSpecial = "%+15s   %+10s   %+15s*"
        if len(self.ClassToFinalDict) == 0:
            print("Class schedule not yet parsed.")
        else:
            print(ppFormatString % ("Class Name", "Final Day", "Final Hours"))
            classVals = list(self.ClassToFinalDict.values())
            self._sortFinalTimes(classVals)
            for time in classVals:
                for key in self.ClassToFinalDict:
                    if self.ClassToFinalDict[key] == time:
                        if time[0] == "TBA":
                            print(ppFormatString % (key, time[0], time[0]))
                        else:
                            if time[2]: ##If isSpecial
                                print(ppFormatStringSpecial % (key, time[0], time[1]))
                                anyIsSpecial = True
                            else:
                                print(ppFormatString % (key, time[0], time[1]))
        if anyIsSpecial:
            print("\n*Final time may have been changed due to conflict. Instructor should announce new final time if applicable.")

    def _getExamScheduleForAnyDay(self, lineSplit):
        for i in lineSplit:
            if i in ExamScheduleInfo.WEEKDAYS:
                day = i
                scheduledTime = " ".join(lineSplit[lineSplit.index(i):])
        return scheduledTime

    def _createRangeForStartTime(self, startRange, isAfternoon):
        addFactor = 0
        if isAfternoon:
            addFactor = 1200
        startRange = startRange.split('-')
        startNum = int(startRange[0].replace(':', "")) + addFactor
        stopNum = int(startRange[1].replace(':', "")) + 1 + addFactor
        return range(startNum, stopNum)

    def _parseFinalTimeToList(self, finalTime, isSpecial):
        if finalTime == "TBA":
            return ["TBA"]
        else:
            finalTimeSpl = finalTime.split()
            timeRange = "".join(finalTimeSpl[1:])
            return [finalTimeSpl[0], timeRange, isSpecial]

    def _getFinalForClassTimeAndDays(self, classTime, classDays):
        for key in self.ExamDictionary:
            if classTime in key:
                if ExamScheduleInfo.KEY_FOR_ANY in self.ExamDictionary[key]:
                    return self._parseFinalTimeToList(self.ExamDictionary[key][ExamScheduleInfo.KEY_FOR_ANY], True)
                if classDays in self.SpecialDays:
                    return self._parseFinalTimeToList(self.ExamDictionary[key][classDays], True)
                else:
                    return self._parseFinalTimeToList(self.ExamDictionary[key][classDays], False)

    ##The efficiency of this sort is probably terrible. But it works.
    def _sortFinalTimes(self, finalTimes):
        sortKeyDict = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "TBA":4, "AM":0, "PM":10}
        changed = True
        while changed: ##Bubble sort best sort
            changed = False
            for idx in range(len(finalTimes)):
                if idx != len(finalTimes) - 1:
                    if sortKeyDict[finalTimes[idx][0]] > sortKeyDict[finalTimes[idx + 1][0]]:
                        finalTimes.insert(idx, finalTimes.pop(idx + 1))
                        changed = True
        changed = True
        while changed:
            changed = False
            for idx in range(len(finalTimes)):
                if idx != len(finalTimes) - 1 and finalTimes[idx][0] != "TBA" and finalTimes[idx+1][0] != "TBA":
                    firstIdxAMorPM = finalTimes[idx][1][-1:-3:-1][::-1]
                    firstIdxStartHr = int(finalTimes[idx][1][0])
                    secondIdxAMorPM = finalTimes[idx+1][1][-1:-3:-1][::-1]
                    secondIdxStartHr = int(finalTimes[idx+1][1][0])
                    if finalTimes[idx][0] == finalTimes[idx+1][0] and (sortKeyDict[firstIdxAMorPM] + firstIdxStartHr) > (sortKeyDict[secondIdxAMorPM] + secondIdxStartHr):
                        finalTimes.insert(idx, finalTimes.pop(idx + 1))
                        changed = True
