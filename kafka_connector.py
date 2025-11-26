"""
Kafka Connector for Python
Based on confluent-kafka library
"""

from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
import json
from typing import Dict, Any, Callable, Optional


class KafkaProducerWrapper:
    """
    Kafka Producer wrapper using confluent-kafka
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092', **config):
        """
        Initialize Kafka Producer
        
        Args:
            bootstrap_servers: Kafka broker address(es)
            **config: Additional producer configuration
        """
        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'python-producer',
            **config
        }
        self.producer = Producer(self.config)
    
    def delivery_report(self, err, msg):
        """
        Callback for message delivery reports
        """
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
    
    def send_message(self, topic: str, value: Dict[str, Any], key: Optional[str] = None):
        """
        Send a message to Kafka topic
        
        Args:
            topic: Kafka topic name
            value: Message value (will be JSON serialized)
            key: Optional message key
        """
        try:
            # Serialize value to JSON
            value_json = json.dumps(value).encode('utf-8')
            key_bytes = key.encode('utf-8') if key else None
            
            # Produce message
            self.producer.produce(
                topic=topic,
                value=value_json,
                key=key_bytes,
                callback=self.delivery_report
            )
            
            # Trigger delivery report callbacks
            self.producer.poll(0)
            
        except Exception as e:
            print(f'Error sending message: {e}')
    
    def flush(self):
        """
        Wait for all messages to be delivered
        """
        self.producer.flush()
    
    def close(self):
        """
        Close the producer
        """
        self.producer.flush()


class KafkaConsumerWrapper:
    """
    Kafka Consumer wrapper using confluent-kafka
    """
    
    def __init__(
        self,
        bootstrap_servers: str = 'localhost:9092',
        group_id: str = 'python-consumer-group',
        topics: list = None,
        **config
    ):
        """
        Initialize Kafka Consumer
        
        Args:
            bootstrap_servers: Kafka broker address(es)
            group_id: Consumer group ID
            topics: List of topics to subscribe to
            **config: Additional consumer configuration
        """
        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            **config
        }
        self.consumer = Consumer(self.config)
        
        if topics:
            self.consumer.subscribe(topics)
    
    def consume_messages(
        self,
        callback: Callable[[Dict[str, Any]], None],
        timeout: float = 1.0,
        max_messages: Optional[int] = None
    ):
        """
        Consume messages from Kafka
        
        Args:
            callback: Function to process each message
            timeout: Timeout for polling in seconds
            max_messages: Maximum number of messages to consume (None for infinite)
        """
        message_count = 0
        
        try:
            while True:
                msg = self.consumer.poll(timeout=timeout)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print(f'End of partition reached {msg.topic()} [{msg.partition()}]')
                    else:
                        raise KafkaException(msg.error())
                else:
                    # Deserialize message
                    try:
                        value = json.loads(msg.value().decode('utf-8'))
                        message_data = {
                            'topic': msg.topic(),
                            'partition': msg.partition(),
                            'offset': msg.offset(),
                            'key': msg.key().decode('utf-8') if msg.key() else None,
                            'value': value
                        }
                        
                        # Process message with callback
                        callback(message_data)
                        
                        message_count += 1
                        
                        if max_messages and message_count >= max_messages:
                            break
                            
                    except Exception as e:
                        print(f'Error processing message: {e}')
                        
        except KeyboardInterrupt:
            print('Consumer interrupted')
        finally:
            self.close()
    
    def close(self):
        """
        Close the consumer
        """
        self.consumer.close()


# Example usage
if __name__ == '__main__':
    # Example Producer
    print("=== Producer Example ===")
    producer = KafkaProducerWrapper(bootstrap_servers='localhost:9092')
    
    # Send some test messages
    for i in range(5):
        message = {
            'id': i,
            'message': f'Test message {i}',
            'timestamp': '2025-11-25'
        }
        producer.send_message(topic='test-topic', value=message, key=f'key-{i}')
    
    producer.flush()
    producer.close()
    print("Messages sent successfully\n")
    
    # Example Consumer
    print("=== Consumer Example ===")
    
    def process_message(msg_data):
        """Process received message"""
        print(f"Received message from {msg_data['topic']}")
        print(f"  Key: {msg_data['key']}")
        print(f"  Value: {msg_data['value']}")
        print(f"  Partition: {msg_data['partition']}, Offset: {msg_data['offset']}\n")
    
    consumer = KafkaConsumerWrapper(
        bootstrap_servers='localhost:9092',
        group_id='test-consumer-group',
        topics=['test-topic']
    )
    
    # Consume messages (will run until interrupted or max_messages reached)
    consumer.consume_messages(callback=process_message, max_messages=5)
