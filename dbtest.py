from sqlalchemy import text
from util.database import engine
from tqdm import tqdm
import requests
import json

# Step 1: Connect to MariaDB using SQLAlchemy

# Function to get the latest last_sent_at value


def get_latest_last_sent_at():
    try:
        with engine.connect() as connection:
            # Query to get the latest last_sent_at value
            # Replace with your actual query
            result = connection.execute(
                text("SELECT MAX(last_sent_at) AS last_sent_at FROM TbKaMessage"))

            row = result.fetchone()
            print(row)
            if row and row[0]:
                return row[0]
            return 0

    except Exception as err:
        print(f"Error retrieving latest last_sent_at: {err}")
        return None


def get_data_from_mariadb(after_timestamp=0):
    try:
       # Establish connection
        with engine.connect() as connection:
            # Execute a query
            result = connection.execute(text("SELECT * FROM mydb_TbKaFeed WHERE sentAt > :after_timestamp ORDER BY sentAt ASC"), {
                                        'after_timestamp': after_timestamp})

            # Fetch all results and convert them to a list of dictionaries
            data = [dict(row._mapping) for row in result]
            # data = [dict(row) for row in result]

        return data

    except Exception as err:
        print(f"Error: {err}")
        return None

# Step 2: Send data to localhost:8000 using POST


def send_data_to_localhost(data):
    url = 'http://localhost:8000/api/kafeed/validate'

    try:
        # Send POST request
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps({
            "room_id": data["roomId"],
            "user_id": data["userId"],
            "chat_id": data["chatId"],
            "client_message_id": data["clientMessageId"],
            "message": data["message"],
            "sent_at": data["sentAt"]
        }), headers=headers)

        # Check for success
        if response.status_code == 200:
            print("Data sent successfully!")
            print("Response body:", response.text)
        else:
            print(f"Failed to send data. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error sending data: {e}")
        print("Response body:", response.text)


if __name__ == "__main__":
    last_sent_at = get_latest_last_sent_at()

    # Step 1: Retrieve data from MariaDB
    data = get_data_from_mariadb(after_timestamp=last_sent_at)
    # print(data)

    if data:
        # Step 2: Send the data to localhost:8000 via POST
        for d in tqdm(data, desc="Sending data", unit="item"):
            send_data_to_localhost(d)
