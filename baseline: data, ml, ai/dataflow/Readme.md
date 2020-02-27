## Qwicklab Dataflow Python

For the setup and project id section, see the ai_platform readme
### Create storage bucket
- As usual

### Virtual env and dataflow sdk
- `sudo pip3 install -U pip`
- `sudo pip3 install --upgrade virtualenv`
- `virtualenv -p python3.7 env`
- `source env/bin/activate`
- install apache-beam `pip install apache-beam[gcp]`


### Run apache beam on local
- run the wordcount.py example: `python -m apache_beam.examples.wordcount --output OUTPUT_FILE`
- see the output result: `ls`
- see the content `cat <file name>`

### Run apache beam on dataflow
- `BUCKET=gs://<bucket name provided earlier>`
- execute: 
```
   python -m apache_beam.examples.wordcount --project $DEVSHELL_PROJECT_ID \
   --runner DataflowRunner \
   --staging_location $BUCKET/staging \
   --temp_location $BUCKET/temp \
   --output $BUCKET/results/output
```
- check the progress on dataflow page
- check the result on $BUCKET/results/output