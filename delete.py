import sqlite3

def delMD(id):
	conn = sqlite3.connect('db.sqlite3')
	c = conn.cursor()

	c.execute("DELETE from CVSMS_storagenodeinfo WHERE id = (?)", id)

	conn.commit()
	conn.close()
 
 
def main(): 
     delMD()

if __name__ == "__main__": 
    main()