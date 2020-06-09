import boto3
import json
import pysftp
import os 
import logging

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def lambda_handler(event, context):
    
    bucket_name = os.environ['BUCKET_NAME']
    sftp_host = os.environ['SFTP_HOST']
    sftp_user = os.environ['SFTP_USER']
    sftp_password_secret_arn = os.environ['SFTP_PASSWORD_SECRET_ARN']
    sftp_file = os.environ['SFTP_FILE']

    # Fetch the password from Secrets Manager
    log.info('Fetching Secret: {}'.format(sftp_password_secret_arn))
    secretsmanager_client = boto3.client(service_name='secretsmanager')
    sftp_password = secretsmanager_client.get_secret_value(SecretId=sftp_password_secret_arn)['SecretString']
    
    with open("/tmp/private_key", "w") as file:
        file.write(sftp_password)
    
        log.info('Connecting to SFTP server: {}'.format(sftp_host))
    cnOpts = pysftp.CnOpts()
    cnOpts.hostkeys = None
    
    #sftp = pysftp.Connection(sftp_host, username=sftp_user, password=sftp_password, cnopts=cnOpts)
    sftp = pysftp.Connection(sftp_host, username=sftp_user, private_key='/tmp/private_key', cnopts=cnOpts)
    
    log.info('Retrieving file: {}'.format(sftp_file))
    sftp.get(sftp_file, localpath='/tmp/sftp_file', preserve_mtime=True)
    
    log.info('Copying file to S3 bucket and path: {}/{}'.format(bucket_name, sftp_file.lstrip('/')))
    s3_client = boto3.client(service_name='s3')
    s3_client = s3_client.put_object(Bucket=bucket_name, Body='/tmp/sftp_file', Key=sftp_file.lstrip('/'))
    
    log.info('Closing connection to SFTP server: {}'.format(sftp_host))
    sftp.close()
    
    
    return True
