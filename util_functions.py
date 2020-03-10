import csv
import os


# TODO: fix relative path from Util dir to steadData Dir
def read_user_ids(path):
    userIds = list()
    with open(path, mode='r') as reader:
        csv_reader = csv.reader(reader)
        first_row_flag = True
        for row in csv_reader:
            if first_row_flag:
                first_row_flag = False
                continue
            userIds.append(int(row[0].split('\t')[0]))
    userIds = list(set(userIds))
    return userIds
