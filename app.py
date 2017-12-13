import boto3
import uuid
from chalice import Chalice

app = Chalice(app_name='pnglabeller')
s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
polly = boto3.client("polly")
bucket = ""
prepend = "audio-files/"
append = ".mp3"

@app.route('/{voice}', content_types=["image/png"], methods=["POST"], cors=True)
def index(voice):
    body = app.current_request.raw_body
    labels = ""
    url = ""
    #Detects labels from png file using AWS Rekognition API
    rekog_response = rekognition.detect_labels(
        Image={
            "Bytes": body
        }
    )
    #Turns rekognition.detect_label response into a simple string
    for label in rekog_response["Labels"]:
        labels += label["Name"] + ", "
    labels = labels[:-2]
    #Generates mp3 file from string of labels
    polly_response = polly.synthesize_speech(
        OutputFormat='mp3',
        Text=labels,
        VoiceId=voice
    )
    #Adds mp3 file to bucket and sets read access to public
    unique_key = prepend + uuid.uuid4().hex[:6].upper() + append
    s3.put_object(
        Bucket=bucket,
        Body=polly_response["AudioStream"].read(),
        Key=unique_key,
        ContentType=polly_response["ContentType"]
    )
    #Creates url to the uploaded mp3 file
    url = "https://s3.amazonaws.com/{0}/{1}".format(bucket, unique_key)
    return {"voice": voice, "labels": labels, "url": url}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
