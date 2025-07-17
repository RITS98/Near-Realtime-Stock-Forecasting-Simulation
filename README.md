# Near Realtime Stock Forecasting Using Docker, Python, Airflow, PostgreSQL and MLOps

A comprehensive data pipeline for stock price forecasting using modern data engineering and machine learning practices. This project demonstrates simulation of near real-time data processing, automated workflows, and predictive analytics for financial data.

## Technologies Used
- **Data Ingestion**: AWS DynamoDB, AWS Kinesis Data Streams, AWS Kinesis Firehose
- **Data Storage**: Amazon S3, AWS Glue, PostgreSQL
- **Data Processing**: AWS Lambda, AWS Glue Jobs
- **Machine Learning**: MLflow, DagsHub, Ray Tune, Pytorch
- **Visualization**: Streamlit, AWS Athena, AWS QuickSight 
- **Orchestration**: Apache Airflow
- **Containerization**: Docker

## Data Used

Historical stock data for Netflix, including features like open, high, low, close prices, volume, and technical indicators.

## Architecture Overview

```mermaid
graph TD
    %% Row 1: Source & Orchestration
    A[📊 Netflix Historical<br/>Stock Data<br/>🐘 PostgreSQL]:::dataSource -->|🔄 Extract & Schedule| B[⏰ Airflow<br/>Scheduler]:::processing
    
    %% Row 2: Real-time CDC Ingestion
    B -->|📡 Push Every Second| C[(🚀 AWS DynamoDB)]:::streaming
    C -->|⚡ CDC Streams| D[🌊 AWS Kinesis<br/>Data Stream]:::streaming
    D -->|🚚 Deliver| E[🔥 Kinesis Firehose<br/>Streaming to S3]:::streaming
    
    %% Row 3: Transformation
    E -->|⚙️ Invoke| F[⚡ AWS Lambda<br/>Transformer]:::processing
    F -->|💾 Store on S3| G[🪣 Amazon S3<br/>Raw CDC Data]:::storage
    
    %% Row 4: Metadata Cataloging
    G -->|🔍 Crawl| H[🕷️ AWS Glue<br/>Crawler]:::storage
    H -->|📋 Register Tables| I[📚 AWS Glue<br/>Data Catalog]:::storage
    
    %% Row 5: Data Lake Optimization
    G -->|🧪 Transform & Write| J[🔥 AWS Glue Job<br/>Hudi Incremental Table]:::processing
    J -->|✅ Output| K[📂 Processed Hudi<br/>Table on S3]:::storage
    K -->|🏗️ Metadata| I

    %% Row 6: Local Download
    K -->|⬇️ Sync Full Dataset| N[💻 Download to Local<br/>via AWS CLI / SDK]:::download

    %% Row 7: ML Workflow
    N -->|🧠 Train Deep Model| O[🧠 Deep Learning Model<br/>📦 MLflow + DagsHub + Ray Tune]:::ml
    O -->|📊 Prediction Results| P[🌐 Streamlit<br/>Dashboard]:::visualization

    %% Subgraphs
    subgraph "🚀 Real-Time Ingestion"
        C --> D --> E
    end

    subgraph "📦 Data Lake & Processing"
        G --> H --> I
        G --> J --> K
    end

    subgraph "📊 Analytics & Insights"
        I --> L[🏛️ AWS Athena]:::analytics --> M[📈 AWS QuickSight]:::visualization
    end

    subgraph "🤖 ML Pipeline"
        N --> O --> P
    end

    %% Styling Classes
    classDef dataSource fill:#00bcd4,stroke:#006064,stroke-width:3px,color:#fff,font-weight:bold
    classDef processing fill:#ba68c8,stroke:#4a148c,stroke-width:3px,color:#fff,font-weight:bold
    classDef streaming fill:#66bb6a,stroke:#1b5e20,stroke-width:3px,color:#fff,font-weight:bold
    classDef storage fill:#ffa726,stroke:#e65100,stroke-width:3px,color:#fff,font-weight:bold
    classDef analytics fill:#f06292,stroke:#880e4f,stroke-width:3px,color:#fff,font-weight:bold
    classDef visualization fill:#aed581,stroke:#33691e,stroke-width:3px,color:#000,font-weight:bold
    classDef download fill:#4fc3f7,stroke:#01579b,stroke-width:3px,color:#000,font-weight:bold
    classDef ml fill:#ffb74d,stroke:#e65100,stroke-width:3px,color:#000,font-weight:bold

    %% Assign Classes
    class A dataSource
    class B,F,J processing
    class C,D,E streaming
    class G,H,I,K storage
    class L analytics
    class M,P visualization
    class N download
    class O ml
```

## Setup Instructions and Results

### Aetup Local Infrastructure
1. Setup PostgreSQL, Apache Airflow and PGAdmin on your local machine using Docker.
2. Clone the repository and navigate to the project directory.
3. Run the following command to start the Airflow web server and scheduler:
   ```bash
   docker-compose up -d
   ```
4. Access the Airflow UI at `http://localhost:8080` and trigger the DAG for real-time data processing.
5. Monitor the logs and outputs in the Airflow UI to ensure everything is functioning correctly
6. The docker-compose code is given below with detailed comments.

```yaml
services:
  # Database Service
  db:
    container_name: postgres_container # Name of the container for the PostgreSQL database.
    image: postgres:14 # Use the official PostgreSQL version 14 image.
    ports:
      - "5001:5432" # Map port 5432 of the container to port 5001 on the host machine.
    environment:
      POSTGRES_USER: ${POSTGRES_USER} # PostgreSQL user, taken from the .env file.
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD} # PostgreSQL password, taken from the .env file.
      POSTGRES_DB: ${POSTGRES_DB} # PostgreSQL database name, taken from the .env file.
    env_file:
      - .env # Specify the environment file to use for setting environment variables.
    volumes:
      - ./postgres/data:/var/lib/postgresql/data # Persist database data to a local directory.
      - ./postgres/airflow_init.sql:/docker-entrypoint-initdb.d/airflow_init.sql # Mount initialization SQL script.
    networks:
      - my_network # Connect this container to the custom network named 'my_network'.

  # Airflow Service
  airflow:
    container_name: airflow_container # Name of the container for Apache Airflow.
    image: apache/airflow:3.0.0 # Use the official Apache Airflow version 3.0.0 image.
    ports:
      - "8001:8080" # Map port 8080 of the container to port 8001 on the host machine.
    environment:
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@db:5432/airflow_db
      # Connection string for Airflow to connect to the PostgreSQL database.
    env_file:
      - .env # Specify the environment file to use for setting environment variables.
    volumes:
      - ./airflow/dags:/opt/airflow/dags # Mount the DAGs directory.
      - ./airflow/logs:/opt/airflow/logs # Mount the logs directory.
      - ./airflow/plugins:/opt/airflow/plugins # Mount the plugins directory.
      - ./code:/opt/airflow/code # Mount a custom code directory.
      - /var/run/docker.sock:/var/run/docker.sock # Mount the Docker socket to allow Airflow to interact with Docker.
      - ./requirements.txt:/opt/airflow/requirements.txt # Mount the Python requirements file.
    depends_on:
      - db # Specify that this service depends on the 'db' service.
    networks:
      - my_network # Connect this container to the custom network named 'my_network'.
    command: >
      bash -c "airflow db migrate &&
      airflow standalone" # Command to run database migrations and start Airflow in standalone mode.

  # pgAdmin Service
  pgadmin:
    image: dpage/pgadmin4 # Use the official pgAdmin 4 image.
    container_name: pgadmin_container # Name of the container for pgAdmin.
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com # Default email for pgAdmin login.
      PGADMIN_DEFAULT_PASSWORD: admin # Default password for pgAdmin login.
    volumes:
      - ./postgres/.pgpass:/pgpass/pgpassfile/.pgpass # Mount the .pgpass file for password management.
    ports:
      - "8055:80" # Map port 80 of the container to port 8055 on the host machine.
    depends_on:
      - db # Specify that this service depends on the 'db' service.
    networks:
      - my_network # Connect this container to the custom network named 'my_network'.

# Define custom networks
networks:
  my_network:
    driver: bridge # Use the bridge driver for the custom network.
```

7. To stop the services, run:
   ```bash
   docker-compose down
   ```

### Setup PostgreSQL Database
1. Create schema and tables in PostgreSQL for storing stock data.
   - Use the provided SQL script `create_schema.sql` to create the necessary schema and tables.
   - Use the provided SQL script `create_tables.sql` to create the necessary tables for stock data.
   - Use the `grant_and_check.sql` script to grant permissions and check the schema.
2. Connect to the PostgreSQL database using pgAdmin or any PostgreSQL client.
3. Run the SQL scripts to set up the database schema and tables.

### Setup Airflow
1. Access the Airflow UI at `http://localhost:8001`.
2. Add AWS credentials
<img width="1680" height="900" alt="image" src="https://github.com/user-attachments/assets/2f104803-360a-4746-97ef-2e2e92287541" />


### Setup AWS S3

1. Create a S3 bucket which holds the raw data from the Change Data Capture from AWS Firehose after apply some transformation using AWS Lambda.
2. Create a second S3 bucket where the actual Hudi data will be stored.
3. The process of creating S3 buckets are shown below
<img width="3410" height="4479" alt="image" src="https://github.com/user-attachments/assets/f11cb05b-540a-486e-8c42-17781028df09" />

<img width="1123" height="475" alt="image" src="https://github.com/user-attachments/assets/87a2461a-1985-499a-b4ff-3ce9d6921b60" />


### Setup AWS DynamoDB

1. Go to Dynamo DB in AWS and click on `Create Table`
2. Fill the information and click on `Create Table`

<img width="1642" height="1523" alt="image" src="https://github.com/user-attachments/assets/ee8fb933-b786-4682-b8c3-94b67347f0c1" />


### Setup AWS Kinesis

1. Go to AWS Kinesis Service and fill the information.
<img width="1656" height="1204" alt="image" src="https://github.com/user-attachments/assets/cdf5d8f4-cbbb-41d9-988a-643d1f48b134" />

<img width="1162" height="366" alt="image" src="https://github.com/user-attachments/assets/3296e953-6f11-40dc-abfc-b8a4957d1d83" />


2. After this we need to go back to Dynamo DB and enable the streaming as shown below.
<img width="1292" height="461" alt="image" src="https://github.com/user-attachments/assets/cda5d248-f67b-48ba-aa05-1149d0fd17cf" />

<img width="1678" height="592" alt="image" src="https://github.com/user-attachments/assets/d57fef88-f658-467c-9cfa-d393fa6b35bd" />

<img width="1684" height="821" alt="image" src="https://github.com/user-attachments/assets/88137196-13ff-41d9-854b-826c8ed50984" />

<img width="1676" height="618" alt="image" src="https://github.com/user-attachments/assets/6725f2ac-0b96-46ea-96a4-cdb41f116963" />

<img width="1670" height="597" alt="image" src="https://github.com/user-attachments/assets/2227f7e0-a23d-45dc-80a8-8c42617a047d" />


### Setup AWS Lambda

1. Setup the lambda.
2. The lambda code does some transformation on the stream data before dumping the data into S3.
<img width="1635" height="919" alt="image" src="https://github.com/user-attachments/assets/a9ce2be0-50b5-4f4c-8114-a6dd3a0a7c6f" />

3. Add the code given below
```
import json
import base64
from datetime import datetime

def lambda_handler(event, context):
    output = []

    for record in event['records']:
        # Decode and parse record
        payload = base64.b64decode(record['data']).decode('utf-8')
        try:
            data = json.loads(payload)

            # Parse DynamoDB NewImage if needed
            if 'dynamodb' in data and 'NewImage' in data['dynamodb']:
                item = data['dynamodb']['NewImage']
                def get_value(attr): return attr.get('S') or attr.get('N')

                transformed = {
                    "stock_symbol": get_value(item['stock_symbol']),
                    "date": get_value(item['date']),
                    "open_price": get_value(item['open_price']),
                    "high_price": get_value(item['high_price']),
                    "low_price": get_value(item['low_price']),
                    "close_price": get_value(item['close_price']),
                    "volume": get_value(item['volume']),
                }

                # Extract year/month for partitioning
                date_obj = datetime.strptime(transformed['date'], "%Y-%m-%d")
                year = date_obj.strftime("%Y")
                month = date_obj.strftime("%m")

                # Add dynamic S3 prefix as metadata
                output.append({
                    'recordId': record['recordId'],
                    'result': 'Ok',
                    'data': base64.b64encode((json.dumps(transformed) + "\n").encode('utf-8')).decode('utf-8'),
                    'metadata': {
                        'partitionKeys': {
                            'year': year,
                            'month': month
                        }
                    }
                })
            else:
                raise Exception("Missing NewImage in record")

        except Exception as e:
            output.append({
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': record['data']
            })

    return {'records': output}
```
4. Click on `Deploy` button.

<img width="1384" height="1925" alt="image" src="https://github.com/user-attachments/assets/ef877391-363e-48a2-ba49-ed7b02b4b58d" />


### Setup AWS Data Firehose

1. Create Data Firehose as shown below

<img width="3276" height="7437" alt="image" src="https://github.com/user-attachments/assets/65b56e87-1d27-4ba6-8365-ac629b8d7f0e" />

2. Add necessary permissions

<img width="1250" height="298" alt="image" src="https://github.com/user-attachments/assets/b8b0f7a5-0d69-41f9-a33f-83541ecc7844" />
<img width="1410" height="698" alt="image" src="https://github.com/user-attachments/assets/bded4120-fc20-4fe1-b367-b443e019a7b1" />

3.  We can see the folders and data
<img width="892" height="442" alt="image" src="https://github.com/user-attachments/assets/c7d962be-8bbc-429c-81df-25d6916d5e46" />

<img width="969" height="768" alt="image" src="https://github.com/user-attachments/assets/4e895b64-2693-49f8-beee-4bf80607b875" />

<img width="1115" height="509" alt="image" src="https://github.com/user-attachments/assets/45047f6a-2993-42af-98ef-a53719eef6d5" />


###  Create a Glue Crawler

1. Crea a Glue Database

<img width="1689" height="424" alt="image" src="https://github.com/user-attachments/assets/a6ea38de-b7c8-4ac3-8d24-4542339150cc" />

2. Create a Classifier for efficient metadata retrieval
<img width="1294" height="665" alt="image" src="https://github.com/user-attachments/assets/cda350e9-0621-47b4-8709-f78bdbc57c0a" />

3. Create a Glue crawler
<img width="1659" height="996" alt="image" src="https://github.com/user-attachments/assets/384be647-f6c6-4e13-b83f-dabdd52614f9" />


### Create Glue ETL Job

1. Create a GLue Visual ETL Job
<img width="1649" height="582" alt="image" src="https://github.com/user-attachments/assets/b9ec122e-28ef-499c-b351-080ff23a5e4b" />


