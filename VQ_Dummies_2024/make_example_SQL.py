import sqlite3
DB_file = "KU_Dummies_VQ_2024.db"

SQLconn = sqlite3.connect(DB_file)
cursor = SQLconn.cursor()
# Database format:
# id: Identification of the json measurement
# json_file_name: name of the json file that contains the electrical measurements from a given run
# assembly_name: name of the assembly
# num_Run: the current run number (default is 1, starting at first run)
# vendor: name of vendor that did the bump bonding (Ex: Micross, Pactech, etc.)
# notes: additional notes
# location: location of where the measurements were taken (KU, FNAL, CERN, etc.)
# humidity: humidity of the environment. Default will be -1, meaning data was not taken
# temperature: temperature of the environment. Default will be -1000, meaning data was not taken
# wire_bonded: 0 if not wire bonded onto a PCB, 1 if wire bonded onto a PCB (Default is 0)
# num_Shear, compression, thermal, other: Number of other tests that have already been performed (default is 0)
json_file_name = "VQ_example_resistance.json"
assembly_name = "assembly_test"
num_Run = 1
vendor = "CNM_Wafer"
notes = "Notes"
location = "KU"
humidity = -1
temperature = -1000
wire_bonded = 0
num_Shear = 0
num_Compression = 0
num_Thermal = 0
num_Other = 0
cursor.execute('''CREATE TABLE IF NOT EXISTS json_files
                      (id INTEGER PRIMARY KEY, json_file_name TEXT, assembly TEXT, num_Run INTEGER, vendor TEXT, notes TEXT, location TEXT, humidity INTEGER, temperature INTEGER, wire_bonded INTEGER, num_Shear INTEGER, num_Compression INTEGER, num_Thermal INTEGER, num_other INTEGER)''')

cursor.execute("INSERT INTO json_files (json_file_name, assembly, num_Run, vendor, notes, location, humidity, temperature, wire_bonded, num_Shear, num_Compression, num_Thermal, num_other) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (json_file_name, assembly_name, num_Run, vendor, notes, location, humidity, temperature, wire_bonded, num_Shear, num_Compression, num_Thermal, num_Other))
SQLconn.commit()
SQLconn.close()
