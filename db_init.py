import sqlite3 

def db_init():
    conn = sqlite3.connect("db/pizzadb.db")
    cursor = conn.cursor()

    cursor.execute("""
                    CREATE TABLE Orders (
                        OrderID BIGINT(15) NOT NULL,
                        ReceiptNo BIGINT(10) NOT NULL,
                        Date DATE,
                        FirstName VARCHAR(20) NOT NULL,
                        LastName VARCHAR(20) NOT NULL,
                        CardNo VARCHAR(16) NOT NULL,
                        TotalCost FLOAT NOT NULL,
                        ACTIVE BOOLEAN NOT NULL,
                        ORDERSERIAL VARCHAR
                    );
                   """)
    
    conn.commit()
    conn.close()

db_init()

