# Handong Feed Validator
> This project is a FastAPI-based system that compares user-inputted messages with existing messages in a database to detect duplicates based on similarity.

## Key Features
- Message similarity calculation using Annoy Index and TF-IDF.
- Database storage of duplicate messages with tracking of duplicate count and original message ID.
- Provides a RESTful API using FastAPI.

## Installation
```shell
pip install -r requirements.txt
```

## Installation and Setup
### 1. Set up a Python virtual environment (optional but recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 2.Install required packages

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a .env file in the project root with the following content:

```env
DB_HOST=<your_db_host>
DB_NAME=<your_db_name>
DB_USERNAME=<your_db_username>
DB_PASSWORD=<your_db_password>
DB_PORT=<your_db_port>  # Default is 3306
```

## Initial Setup
### 1. Generate Annoy Index and TF-IDF Vectorizer

First, run the `build_annoy_index.py` script to create the Annoy index and TF-IDF vectorizer model.    
This script will load existing messages from the database and build the index by vectorizing the messages.

```bash
python util/build_annoy_index.py
```
After running this script, the `artifacts/` folder will contain the `annoy_index.ann` and `tfidf_vectorizer.pkl` files.

### 2. Run the Server

Once everything is set up, you can run the FastAPI server:

```bash
uvicorn main:app --reload
```
The server will run by default at http://127.0.0.1:8000.

## API Documentation
### `/api/kafeed/validate` (POST)
#### Description
>Receives a user-submitted message and checks for duplication by comparing it with existing messages in the database.

#### Request Body
```json
{
    "chat_id": 1234567890,
    "client_message_id": 1234567890,
    "room_id": 1234567890,
    "sent_at": 1609459200,
    "user_id": 1234567890,
    "message": "Your message text here"
}
```
#### Response:
- If the message is a duplicate
    ```json
    {
        "message_id": "26970924ffb244be839774a32576b4bb",
        "message": "Your message text here",
        "is_duplicate": true,
        "original_id": "06e61bda7f204ebb9819fdeee55e62fa",
        "distance": 0.1234,
        "duplicate_count": 1
    }
    ```
- If the message is not a duplicate
    ```json
    {
        "message_id": "26970924ffb244be839774a32576b4bb",
        "message": "Your message text here",
        "is_duplicate": false
    }
    ```

## Notes
- Ensure that the build_annoy_index.py script is run every time the message database is updated significantly, to keep the Annoy index up to date.
- The threshold for considering a message as a duplicate can be adjusted in the ValidateService class within the code.