import weaviate
import json

client = weaviate.connect_to_local()

questions = client.collections.get("Question")
response = questions.query.hybrid(
    query="blood",
    limit=2,
)

for obj in response.objects:
    print(json.dumps(obj.properties, indent=2))

client.close()  # Free up resources