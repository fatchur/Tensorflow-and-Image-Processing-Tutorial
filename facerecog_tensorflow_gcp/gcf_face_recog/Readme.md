# Note
In this section, we will make a face searcher based on the incoming face feature and face dataset in bigquery.

## Steps 
### Then create the cloud function 
- On the spot explanantion

### Horey, test ypur function now
- endpoint (on the spot explanation)
- Request format
```python
{"task":"search", "info":{"name":"jkw"}, "image": base64 string image}
```
- Response format
```python
{
    "data": {
        "rank1": {
            "id": "b1ae2f62-e29a-11e9-9653-6ff33e7dded4",
            "name": "jkw",
            "distance": 0
        },
        "rank2": {
            "id": "2d4e9d3a-e2a7-11e9-9ebe-e9f2c2f2bd06",
            "name": "jkw",
            "distance": 0
        },
        "rank3": {
            "id": "3369d13a-e2a7-11e9-9ebe-e9f2c2f2bd06",
            "name": "jkw",
            "distance": 0
        }
    },
    "message": "searching face identity: success"
}
```


