import openpyxl
import re

def extract_channels_from_xlsx(filename):
    channels = set()
    wb = openpyxl.load_workbook(filename)
    ws = wb.active
    for row in ws.iter_rows(values_only=True):
        for cell in row:
            if isinstance(cell, str):
                matches = re.findall(r'(?:@|https?://t\.me/|https?://telegram\.me/)(\w+)', cell)
                # print("Cell:", cell)
                # print("Matches:", matches)
                channels.update(matches)
    return channels

def save_channels_to_file(channels, output_file):
    with open(output_file, 'w') as file:
        file.write('\n'.join(channels))

# Replace 'channels.xlsx' with the actual path to your channels.xlsx file
channels_file = 'channels.xlsx'
output_file = 'channels.txt'

extracted_channels = extract_channels_from_xlsx(channels_file)
save_channels_to_file(extracted_channels, output_file)
