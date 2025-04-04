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
    
    cursor.execute("""
                    CREATE TABLE ReceiptItems(
                        ReceiptNo BIGINT(10) NOT NULL,
                        OrderID BIGINT(15) NOT NULL,
                        ItemID BIGINT(10),
                        ItemName VARCHAR(25),
                        ItemCost FLOAT
                    );
                   """)
    cursor.execute(""" 
                    CREATE TABLE Item(
                    ItemID BIGINT(10),
                    ItemName VARCHAR(25),
                    ItemCost FLOAT,
                    ItemImageURL
                   );
                   """)
    cursor.execute("INSERT INTO Item VALUES (1000000000,'Cheese Pizza',10.99, 'static/pepperoni_pizza.png');")
    cursor.execute("INSERT INTO Item VALUES (1000000001,'Pepperoni} Pizza',11.99, 'static/pepperoni_pizza.png');")
    cursor.execute("INSERT INTO Item VALUES (1000000002,'Sausage Pizza',11.99, 'static/pepperoni_pizza.png');")
    cursor.execute("INSERT INTO Item VALUES (1000000003,'BBQ Chicken Pizza', 13.99, 'static/pepperoni_pizza.png');")
    cursor.execute("INSERT INTO Item VALUES (1000000004,'Calzone',7.99, 'static/pepperoni_pizza.png');")
    cursor.execute("INSERT INTO Item VALUES (1000000005,'Brownie',8.99, 'static/pepperoni_pizza.png')")

    conn.commit()
    conn.close()

db_init()

