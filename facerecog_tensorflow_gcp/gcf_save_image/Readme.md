# Note
In this section, we will make a fuction for saving the face image from pubsub to the GCS.

## Steps
### Create face image bucket storage (GCS)
- search and go to `storage`
- choose `create bucket` on the top section
- set the name of your face image bucket (MUST unique) 

### Create cloud pub/sub topic 
- go to `Pub/Sub`
- select `create topic` ont the top section
- SET `save_image` as yout topic name

### Then create the cloud function (image saver)
- edit "face_recog_image" in `bucket = client.bucket("face_recog_image")` in `main.py` based on your bucket name
- On the spot explanation

### Horey, test ypur function now
- click your pubsub topic name
- click `publis message` on the top section
- copy the **base64 string image** over there then click `publish` button

