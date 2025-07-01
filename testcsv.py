import csv
from Settings import Settings

sett = Settings()
unique_footprints = set()

with open('D:\\2\\Pick Place for SiC_DRV_PSUv0.1.0_processed.csv', newline='') as file:
    reader = csv.DictReader(file)
    coloumns_header = sett.load('coloumns')

    for row in reader:
        ftp = 'Footprint'
        footprint = row[ftp].strip()
        Rotation = row['Rotation'].strip()
        FeedT = row['FeedT'].strip()
        print(f'f = {footprint}, r = {Rotation}, ft = {FeedT}')
        unique_footprints.add(footprint)

#print(unique_footprints)
