import os

def download_files(links):

#1. Ask for full path of the directory where the files are to be saved.
    save_path = input('Enter the full path of directory you want to save the files in: ')

#TODO: Make a directory for the course for which download is being done, go into this directory
#TODO: Store the slot for the current course
#TODO: Check the current time stamp, compare it with the timestamps of CAT-1, CAT-2 and FAT exams for that particular course using the slot of the course and the start date of the exam-event
#TODO: If current_ts <= CAT1_ts => make a directory as CAT-1 and save all the files in it. If CAT_ts<current_ts<=CAT-2_ts, then make a directory as CAT-2 and download the files in it. If current_ts>CAT-2, make a directory FAT and download the files in it
#TODO: Return the number of files downloaded
