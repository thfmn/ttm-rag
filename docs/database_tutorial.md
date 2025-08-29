# Database Interaction Tutorial

This tutorial explains how to interact with the project's database, whether you are using SQLite for development or PostgreSQL in a Docker container.

## 1. Database Setup

First, ensure your database is set up correctly.

### For SQLite (Default for Development)
If you are using the default SQLite database, you just need to run the setup command:
```bash
make db-setup
```
This will create the `thai_medicine.db` file in the project root and run all necessary migrations.

### For PostgreSQL (Docker)
1.  **Start the Docker container:**
    ```bash
    docker-compose up -d db
    ```
2.  **Update your `.env` file:**
    Change the `DATABASE_URL` to point to the PostgreSQL container:
    ```
    DATABASE_URL=postgresql://user:password@localhost:5432/thai_medicine_db
    ```
3.  **Run the setup command:**
    ```bash
    make db-setup
    ```

## 2. Connecting to the Database

You can connect directly to the database to inspect the data.

### Connecting to SQLite
You can use the `sqlite3` command-line tool:
```bash
sqlite3 thai_medicine.db
```
Once connected, you can run SQL queries. For example, to see all tables:
```sql
.tables
```
To see the schema of a table:
```sql
.schema chunk_embeddings
```
To count the number of chunks:
```sql
SELECT COUNT(*) FROM chunk_embeddings;
```
To exit, type `.quit`.

### Connecting to PostgreSQL (Docker)
You can get a shell inside the running PostgreSQL container:
```bash
docker-compose exec db psql -U user -d thai_medicine_db
```
- `-U user`: Connects as the `user` user.
- `-d thai_medicine_db`: Connects to the `thai_medicine_db` database.

Once connected, you can run SQL queries. For example, to see all tables:
```sql
\dt
```
To see the schema of a table:
```sql
\d chunk_embeddings
```
To count the number of chunks:
```sql
SELECT COUNT(*) FROM chunk_embeddings;
```
To exit, type `\q`.

## 3. Understanding the Key Tables

### `documents` Table
This table is not used in the RAG implementation.

### `chunk_embeddings` Table
This is the most important table for the RAG system. It stores the text chunks and their corresponding vector embeddings.

**Key Columns:**
- `id`: The primary key.
- `chunk_id`: A unique identifier for the chunk.
- `document_id`: The ID of the document the chunk belongs to.
- `content`: The actual text of the chunk.
- `chunk_index`: The order of the chunk within the document.
- `embedding`: The vector embedding of the chunk's content. This is what's used for similarity search.
- `chunk_metadata`: A JSON field for storing additional metadata about the chunk.

**Sample Queries:**
- **Find all chunks for a specific document:**
  ```sql
  SELECT * FROM chunk_embeddings WHERE document_id = 'your-doc-id';
  ```
- **Get the content of a specific chunk:**
  ```sql
  SELECT content FROM chunk_embeddings WHERE chunk_id = 'some-chunk-id';
  ```

## 4. Database Management Scripts

The project includes several `make` commands to help manage the database.

- `make db-setup`: Creates the database and tables, and seeds it with initial data.
- `make db-create`: Creates the database and tables.
- `make db-seed`: Seeds the database with initial data.
- `make db-drop`: **WARNING: This will delete all data in your database.**
- `make db-reset`: A combination of `db-drop`, `db-create`, and `db-seed`.

These scripts are useful for development and testing, allowing you to quickly reset the database to a clean state.
