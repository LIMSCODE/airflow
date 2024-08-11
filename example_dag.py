from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime, timedelta
import json

default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024,8,11),
        'retries':1,
        'retry_delay': timedelta(minutes=5),
}

dag = DAG(
        'kafka_airflow_dag',
        default_args=default_args,
        description='A simple kafka and airflow dag',
        schedule=timedelta(minutes=10),
)

# consume_from_kafka 태스크에서 이 메시지를 소비
def consume_from_kafka(**kwargs):
    consumer = KafkaConsumer(
            'topic3',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            group_id='my-group',
    )
    for message in consumer:
        data = message.value.decode('utf-8')
        print(f"Consumed message: {data}")

# produce_to_kafka 태스크에서 Kafka 토픽에 메시지를 생성
def produce_to_kafka(**kwargs):
    producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )
    for i in range(10):
        producer.send('topic3', {'message': f'Hello {i}'})
    producer.flush()

produce_task = PythonOperator(
        task_id='produce_to_kafka',
        python_callable=produce_to_kafka,
        dag=dag,
)

consume_task = PythonOperator(
        task_id='consume_from_kafka',
        python_callable=consume_from_kafka,
        dag=dag,
)

produce_task >> consume_task

# Airflow 웹에서 kafka_airflow_dag DAG를 활성화하고 실행 


 
