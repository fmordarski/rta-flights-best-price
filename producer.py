import json
from time import sleep

from kafka import KafkaProducer


if __name__ == "__main__":
    server = "localhost:9092"

    producer = KafkaProducer(
        bootstrap_servers=[server],
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        api_version=(2, 7, 0),
    )

    with open("data/final.json", "r") as f:
        data = json.load(f)

    try:
        for i in range(len(data["Origin"])):
            message = {
                "Origin": data["Origin"][i],
                "Destination": data["Destination"][i],
                "Price": data["Price"][i],
                "Date": data["Date"][i],
                "Carrier": data["Carrier"][i]
            }
            producer.send("flights", value=message)
            sleep(0.1)
    except KeyboardInterrupt:
        producer.close()
