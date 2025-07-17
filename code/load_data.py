import psycopg2
import os
import csv

def load_data():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'stock_data'),
            user=os.getenv('DB_USER', 'stock_user'),
            password=os.getenv('DB_PASSWORD', 'stock_pass'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5001')
        )

        with connection:
            with connection.cursor() as cursor:
                # Load data from CSV file
                csv_file_path = os.path.join(os.path.dirname(__file__), '../netflix_historical_data', 'Netflix_stock_data.csv')

                with open(csv_file_path, 'r') as f:
                    csv_reader = csv.reader(f)
                    next(csv_reader)  # Skip the header row

                    for row in csv_reader:
                        if len(row) >= 6:  # Ensure there are enough columns
                            cursor.execute(
                                "INSERT INTO netflix_historical.stock_prices (stock_symbol, date, open_price, high_price, low_price, close_price, volume) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                ('NFLX', row[0], float(row[4]), float(row[2]), float(row[3]), float(row[1]), int(row[5]))
                            )

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    load_data()
