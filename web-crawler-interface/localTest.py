import sqlite3

sqliteConnection = sqlite3.connect(r'database/LocalDataBase.db')
cursor = sqliteConnection.cursor()

sqlite_select_Query ="SELECT * FROM LocalData"

# sqlite_select_Query ="DROP TABLE LocalData"

# sqlite_select_Query ='''CREATE TABLE LocalData (
# 	WebsiteId TEXT,
# 	State TEXT,
# 	City TEXT,
# 	Pin TEXT,
# 	Increment INTEGER,
# 	RowCount TEXT,
# 	LastRun TEXT,
#     Change INTEGER
# );'''

# babu = 'Luminous'
# sqlite_select_Query = f'''SELECT * FROM LocalData where WebsiteId='Luminous';'''

# sqlite_select_Query = '''INSERT INTO LocalData
# VALUES ('Fssai', 'ANDA', 'Port', '101011', 0, '16,51,141', '7 May', 0, -1);'''


sqlite_select_Query = '''UPDATE LocalData
SET State='-', City='-', LastRun = '7 May', RowCount='16,51,141'
WHERE WebsiteId = 'Fssai';'''

# sqlite_select_Query = '''UPDATE LocalData
# SET Condition=-1
# WHERE WebsiteId='Daikin';'''

# sqlite_select_Query = '''ALTER TABLE LocalData
# RENAME COLUMN Error TO Condition;'''

# sqlite_select_Query = "DELETE FROM LocalData WHERE WebsiteId='Malabar';"

# sqlite_select_Query = "ALTER TABLE LocalData ADD COLUMN Error INTEGER;"



cursor.execute(sqlite_select_Query)
record = cursor.fetchall()
print(record)

sqliteConnection.commit()
cursor.close()
