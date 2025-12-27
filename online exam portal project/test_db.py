from database import get_db
try:
    db=get_db()
    print("database connected successfully")
    db.close()
except Exception as e:
    print("not connected",e)