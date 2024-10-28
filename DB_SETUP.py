import psycopg2
from sentence_transformers import SentenceTransformer

# Database connection parameters
database = "shopping_data"
user = "postgres"
password = "<Password>"
host = "localhost"

def connect_db(dbname):
    """
    Connect to the specified PostgreSQL database.
    
    Args:
        dbname (str): The name of the database to connect to.
    
    Returns:
        conn: A connection object to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        return conn
    except Exception as e:
        print(f"Error connecting to Database {dbname}: ", e)

# Step 1: Connect to the 'postgres' database to check for 'shopping_data' existence
conn = connect_db("postgres")
cursor = conn.cursor()

# Check if the database exists
cursor.execute("""
    SELECT EXISTS(
        SELECT datname FROM pg_database WHERE datname = %s
    )
""", (database,))
db_exists = cursor.fetchone()[0]

# Create the database if it does not exist
if not db_exists:
    cursor.execute(f"CREATE DATABASE {database}")
    conn.commit()
    print(f"Database '{database}' created successfully.")

# Close initial connection and reconnect to the new database
cursor.close()
conn.close()

# Step 2: Connect to the new 'shopping_data' database
conn = connect_db(database)
cursor = conn.cursor()

# Enable 'vector' extension if not already installed
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
conn.commit()

# Check if 'apparels' table exists
cursor.execute("""
    SELECT EXISTS(
        SELECT 1 FROM information_schema.tables WHERE table_name = 'apparels'
    )
""")
table_exists = cursor.fetchone()[0]

# Create 'apparels' table if it does not exist
if not table_exists:
    cursor.execute("""
        CREATE TABLE apparels (
            id SERIAL PRIMARY KEY,        -- Unique identifier for each product
            category VARCHAR,             -- Product category
            sub_category VARCHAR,          -- Sub-category of the product
            uri VARCHAR,                  -- URI for product
            image VARCHAR,                -- URI for the product image
            content VARCHAR,              -- Additional product content or description
            pdt_desc VARCHAR,             -- Detailed description of the product
            embedding VECTOR              -- Vector for embedding
        )
    """)
    conn.commit()
    print("Table 'apparels' created successfully.")

# Step 3: Insert data from CSV file
try:
    cursor.execute("""
        COPY apparels (category, sub_category, uri, image, content)
        FROM '/path/to/your/data.csv'  -- Specify the correct path to your CSV file
        DELIMITER ','
        CSV HEADER;
    """)
    conn.commit()
    print("Data imported successfully from CSV.")
except Exception as e:
    print("Error during CSV import: ", e)

# Step 4: Update 'pdt_desc' with a concatenated description
cursor.execute("""
    UPDATE apparels 
    SET pdt_desc = CONCAT(
        'This product category is: ', category, 
        ' and sub_category is: ', sub_category, 
        '. The description of the product is as follows: ', content, 
        '. The product image is stored at: ', uri
    ) 
    WHERE id IS NOT NULL;  -- Ensure we only update rows that have an id
""")
conn.commit()
print("Product descriptions updated successfully.")

# Step 5: Generate embeddings for each product description
model = SentenceTransformer('all-MiniLM-L6-v2')  # Load the pre-trained embedding model

try:
    cursor.execute("SELECT id, pdt_desc FROM apparels")  # Fetch product IDs and descriptions
    rows = cursor.fetchall()

    for row in rows:
        id = row[0]  # Extract the product ID
        description = row[1]  # Extract the product description

        # Generate embedding for the product description
        embedding = model.encode(description).tolist()  # Convert to list for PostgreSQL compatibility
        
        # Update the embedding in the database
        cursor.execute(
            "UPDATE apparels SET embedding = %s WHERE id = %s", (embedding, id)
        )
        print(f"Embedding for ID {id} generated and updated successfully.")

    conn.commit()  # Commit all updates after processing
    print("All embeddings generated and updated successfully.")

except Exception as e:
    print(f"An error occurred during embedding generation: {e}")

finally:
    # Close the cursor and connection
    cursor.close()
    conn.close()
