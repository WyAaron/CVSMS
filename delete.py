import sqlite3

def delMD():
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("DELETE FROM CVSMS_storagenodeinfo " )

	conn.commit()
	conn.close()
 
 
def storageStateFail(SID): 
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute("UPDATE CVSMS_storagenodeinfo SET status = ? WHERE SID = ?",(True,SID))
    print(f'{SID} - offline')
    conn.commit()
    conn.close()
 
def main(): 
		storageStateFail("Test-PC2")

if __name__ == "__main__": 
    main()