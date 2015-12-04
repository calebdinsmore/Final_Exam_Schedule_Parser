from ExamScheduleInfo import *

examSched = ExamScheduleInfo("parsed-exam-times.txt")

examSched.fillDictionary()

d = examSched.parseClassSchedule("MyClassSchedule.txt")

examSched.prettyPrintClassToFinalDate()
