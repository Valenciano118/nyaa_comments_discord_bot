import mariadb
import sys 
class MariaDB():
    def __init__(self, config:dict[str,str]):
        try:
            user = config['db_user']
            password = config['db_password']
            host = config['db_host']
            port = int(config['db_port'])
            database = config['db_name']
        except:
            print("Error parsing config, make sure your MariaDB configuration is correct")
        
        try:
            conn = mariadb.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database
            )
        except mariadb.Error as e:
            print(f"Error connecting to the MariaDB Platform: {e}")
            sys.exit(1)
        self.conn = conn
    