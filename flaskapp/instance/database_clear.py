from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker


# Create an engine and connect to the database
engine = create_engine('sqlite:///database1.db')

Session = sessionmaker(bind=engine)
session = Session()

# Get metadata and reflect it from the database
meta = MetaData()
meta.reflect(bind=engine)

# Truncate all tables
with session.begin():
    for table in meta.sorted_tables:
        print(f"Table: {table.name}")
        
        # # Select all rows from the table
        # select_stmt = table.select()
        # result = session.execute(select_stmt)

        # # Print out each row
        # for row in result:
        #     print(row)
        session.execute(table.delete())

session.commit()

