from chalice import Chalice,BadRequestError, Response
import boto3
import json
import requests

app = Chalice(app_name='upload-batchfile')
sqs = boto3.client('sqs')

FILE_QUEUE_NAME = 'filequeue'
FILE_QUEUE_URL = 'https://sqs.eu-central-1.amazonaws.com/782346665958/filequeue'
PARTNER_API = "https://pxlnwwd545.execute-api.us-east-2.amazonaws.com/api/buckets/"

@app.on_sqs_message(queue=FILE_QUEUE_NAME)
def on_event(event):
    for record in event:
        print("new message record:", record.body)
        f = json.loads(record.body)
        if "-" not in f["id"]:
            return
            
        bId = f["id"].split("-")
        del f["id"]
        try :
            resp = requests.patch(PARTNER_API + f[0] + "/files/" + f[1], json=f)
            print(resp.text)
        except Exception as e:
            print("An error occured:", str(e))
            sqs.send_message(
                QueueUrl=FILE_QUEUE_URL,
                MessageBody=record.body
            )

@app.route('/batch-upload', methods=['POST'])
def batch_upload():
    try:
        file_list = app.current_request.json_body
        for f in file_list: 
            #check data type.
            sqs.send_message(
                QueueUrl=FILE_QUEUE_URL,
                MessageBody=json.dumps(f)
            )
        
        return Response(body='{"message": "started batch file to update."}',
                        status_code=202)

    except Exception as e:
        raise BadRequestError("An error occured: %s" % str(e))
