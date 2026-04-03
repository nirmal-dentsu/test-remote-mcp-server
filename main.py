import psycopg2
import os
from fastmcp import FastMCP
"""Schema for the expenses table
                                CREATE TABLE IF NOT EXISTS expenses (
                                    id SERIAL PRIMARY KEY,
                                    date DATE NOT NULL,
                                    amount NUMERIC NOT NULL,
                                    category TEXT NOT NULL,
                                    subcategory TEXT DEFAULT '',
                                    note TEXT DEFAULT ''
);"""

mcp=FastMCP(name="Expense Tracker")

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(
    DATABASE_URL,
    sslmode="require"
)

print("Connected successfully!")


category_path=os.path.join(os.path.dirname(__file__),"categories.json")

@mcp.tool
def add_expense(date,amount,category,subcategory="",note=""):
    """Add a new expense entry to database."""
    cursor=conn.cursor()
    try:
        cursor.execute("INSERT INTO expenses(date,amount,category,subcategory,note) VALUES(%s,%s,%s,%s,%s)",(date,amount,category,subcategory,note))
        new_id=cursor.fetchone()[0]
        conn.commit()
        return{"Status":"ok","id":new_id}
    except Exception as e:
        return e
        
@mcp.tool
def list_expenses(start_date,end_date):
    """List all expenses entries from database"""
    cursor=conn.cursor()
    cursor.execute("select * from expenses where date BETWEEN %s AND %s ORDER BY id ASC",(start_date,end_date))
    column=[d[0] for d in cursor.description]
    rows=cursor.fetchall()
    return[dict(zip(column,row)) for row in rows]
    

@mcp.tool
def summarize(start_date,end_date,category=None):
    """This is a tool which summarizes expenses by category"""
    cursor=conn.cursor()
    query=("Select category,sum(amount) as Total_amount from expenses where date BETWEEN %s AND %s")
    parameter=[start_date,end_date]
    if category:
        query+="AND category=%s"
        parameter.append(category)
    query+="Group by category Order by category ASC"
    
    cursor.execute(query,parameter)
    print(cursor.description)
    column=[col[0] for col in cursor.description]
    rows=cursor.fetchall()
    return([dict(zip(column,row)) for row in rows])

@mcp.resource("expense://categories",mime_type="application/json")
def categories():
    with open(category_path,"r",encoding="utf-8") as f:
        return f.read()

if __name__=="__main__":
    port = int(os.environ.get("PORT", 8000))   # ✅ IMPORTANT
    mcp.run(transport="http", host="0.0.0.0", port=port)
    # mcp.run(transport="http",host="0.0.0.0",port=8000)