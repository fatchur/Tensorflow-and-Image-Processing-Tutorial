from google.cloud import bigquery


def create_feature_column(schema_list):
    for i in range(512):
        schema_list.append(bigquery.SchemaField("feature"+str(i), "FLOAT", mode="REQUIRED"))
    return schema_list


schema = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED")]

schema = create_feature_column(schema)
print (schema)

client = bigquery.Client()
table_id = "braided-grammar-239803.face.face_features"
table = bigquery.Table(table_id, schema=schema)
table = client.create_table(table)  # API request
print(
    "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
)
