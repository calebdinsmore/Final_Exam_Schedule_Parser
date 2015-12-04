import os, time

inFile="exams.pdf"
tempFile="temp-exams.txt"
outFile="parsed-exam-times.txt"
os.system(("ps2ascii %s %s ") %(inFile, tempFile))

os.system(("perl -p -e 's/[[:^ascii:]]//g' < %s > %s && rm %s") %(tempFile, outFile, tempFile)) ##strips bad characters from .txt
