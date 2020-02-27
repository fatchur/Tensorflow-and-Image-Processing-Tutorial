## AI Platform Qwicklab Note
### Setup
- Enroll the quest
- Select the AI platform
- Click `start lab`
- Choose using token or credits
- you will get the `username email`, `password`, `project-id`

### GCP Console
- go to GCP console
- see the service account `gcloud auth list`
- get the current project id `gcloud config list project`


### Create virtual env
- `sudo apt-get update`
- `sudo apt-get install virtualenv`
- `virtualenv -p python3 venv`
- `source venv/bin/activate`

### Clone the repository
- `git clone https://github.com/GoogleCloudPlatform/cloudml-samples.git`
- `cd cloudml-samples/census/estimator`

### Prepare Training Locally
- create data directory `mkdir data`
- download data form gcs `gsutil -m cp gs://cloud-samples-data/ml-engine/census/data/* data/`
- generate train and val env variable 
```
export TRAIN_DATA=$(pwd)/data/adult.data.csv
export EVAL_DATA=$(pwd)/data/adult.test.csv
```
- verify the downloaded data `head data/adult.data.csv`
- install dependencies `pip install -r ../requirements.txt`
- update pandas `pip install pandas==0.24.2`
- Verify TF version 
```
python -c "import tensorflow as tf; print('TensorFlow version {} is installed.'.format(tf.__version__))"
```

### Run Local Training
- `export MODEL_DIR=output`
- ```gcloud ai-platform local train \
    --module-name trainer.task \
    --package-path trainer/ \
    --job-dir $MODEL_DIR \
    -- \
    --train-files $TRAIN_DATA \
    --eval-files $EVAL_DATA \
    --train-steps 1000 \
    --eval-steps 100
    ```
- see the output `ls output/export/census/`, then you will get timestamp folder
- predict the test data with the result model 
```
    gcloud ai-platform local predict \
    --model-dir output/export/census/<timestamp> \
    --json-instances ../test.json
```

- IF error run this 
```
sudo rm -rf /google/google-cloud-sdk/lib/googlecloudsdk/command_lib/ml_engine/*.pyc
```

### Prepare Cloud Training 
- ```
  PROJECT_ID=$(gcloud config list project --format "value(core.project)")
  BUCKET_NAME=${PROJECT_ID}-mlengine
  echo $BUCKET_NAME
  REGION=us-central1
  ```
- create bucket `gsutil mb -l $REGION gs://$BUCKET_NAME`
- copy the local data to gcs `gsutil cp -r data gs://$BUCKET_NAME/data`
- create env name for train dan val data
```
    TRAIN_DATA=gs://$BUCKET_NAME/data/adult.data.csv
    EVAL_DATA=gs://$BUCKET_NAME/data/adult.test.csv
```
- copy test json to gcs `gsutil cp ../test.json gs://$BUCKET_NAME/data/test.json`
- create test env variable `TEST_JSON=gs://$BUCKET_NAME/data/test.json`
- set job name env variable `JOB_NAME=census_single_1`
- set bucket output path `OUTPUT_PATH=gs://$BUCKET_NAME/$JOB_NAME`
- Run training:
```
    gcloud ai-platform jobs submit training $JOB_NAME \
    --job-dir $OUTPUT_PATH \
    --runtime-version 1.14 \
    --python-version 3.5 \
    --module-name trainer.task \
    --package-path trainer/ \
    --region $REGION \
    -- \
    --train-files $TRAIN_DATA \
    --eval-files $EVAL_DATA \
    --train-steps 1000 \
    --eval-steps 100 \
    --verbosity DEBUG
```

- see the training progress `gcloud ai-platform jobs stream-logs $JOB_NAME`
- see the output in gcs `gsutil ls -r $OUTPUT_PATH`


### Deploy Model
- set the model name `MODEL_NAME=census`
- create the AI platfor model `gcloud ai-platform models create $MODEL_NAME --regions=$REGION`
- check the ready to deploy model `gsutil ls -r $OUTPUT_PATH/export`, then you will get timestamp folder.
- model env var `MODEL_BINARIES=$OUTPUT_PATH/export/census/<timestamp>/`
- deploy the model with versin v1
```
    gcloud ai-platform versions create v1 \
    --model $MODEL_NAME \
    --origin $MODEL_BINARIES \
    --runtime-version 1.14 \
    --python-version 3.5
```
- once your model is ready, test the model
```
    gcloud ai-platform predict \
    --model $MODEL_NAME \
    --version v1 \
    --json-instances ../test.json
```







