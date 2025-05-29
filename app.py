from flask import Flask, render_template, request, redirect, url_for
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# AWS S3 client setup
s3 = boto3.client("s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

app = Flask(__name__)

@app.route('/')
def index():
    # List files in the bucket
    objects = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    file_list = [obj['Key'] for obj in objects.get('Contents', [])]
    return render_template('index.html', files=file_list)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        s3.upload_fileobj(file, S3_BUCKET_NAME, file.filename)
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    file_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': filename},
        ExpiresIn=300  # valid for 5 minutes
    )
    return redirect(file_url)

@app.route('/delete/<filename>')
def delete(filename):
    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)