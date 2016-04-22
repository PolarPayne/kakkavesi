from db_connection import connection



class Target:

    def __init__(self, keys, vals):
        for i in range(0, len(keys)):
            setattr(self, keys[i], vals[i])



def get_targets():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM [AWR].[dbo].[HSY_TARGETS]")

    keys = [x[0].lower() for x in cursor.description]
    rows = cursor.fetchall()

    return [Target(keys, x) for x in rows]



