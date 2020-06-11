import boto3
import json
import pysftp
import os 
import logging
import fnmatch
from stat import S_ISDIR, S_ISREG


logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#boto3.set_stream_logger('')

def lambda_handler(event, context):
    log.debug(event)
    
    bucket_name = event.get('TargetBucketName')
    sftp_host = event.get('SftpHost')
    sftp_user = event.get('SftpUser')
    sftp_password_secret_arn = event.get('SftpSecretArn')
    sftp_private_key_auth = event.get('SftpPrivateKeyAuth', 'False').lower() == 'true'
    sftp_files = event.get('Files')
    

    # Fetch the password from Secrets Manager
    log.info('Fetching Secret: {}'.format(sftp_password_secret_arn))
    secretsmanager_client = boto3.client(service_name='secretsmanager')
    sftp_password = secretsmanager_client.get_secret_value(SecretId=sftp_password_secret_arn)['SecretString']
    log.info('Retrieved secret')

    cnOpts = pysftp.CnOpts()
    cnOpts.hostkeys = None
    log.info('Connecting to SFTP server: {}'.format(sftp_host))    
    if sftp_private_key_auth:
        with open("/tmp/private_key", "w") as file:
            file.write(sftp_password)
        sftp = pysftp.Connection(sftp_host, username=sftp_user, private_key='/tmp/private_key', cnopts=cnOpts)
        os.remove('/tmp/private_key')
    else:
        sftp = pysftp.Connection(sftp_host, username=sftp_user, password=sftp_password, cnopts=cnOpts)
    
    for sftp_file in sftp_files:
        log.info ('SourceFile: {}'.format(sftp_file.get('SourceFile')))
        log.info ('TargetPath: {}'.format(sftp_file.get('TargetPath')))
        path, file = sftp_file.get('SourceFile').rsplit('/', 1)
        target_path = sftp_file.get('TargetPath')
        log.info ('Retrieving directory list for path: {} '.format(path))
        sftp_list_dir_attr = sftp.listdir_attr(path)
        log.debug("Directory listing: {}".format(sftp_list_dir_attr))
        for entry in sftp_list_dir_attr:
            # If filename matches pattern AND is not a directory AND is a regular file
            if fnmatch.fnmatch(entry.filename, file) and not S_ISDIR(entry.st_mode) and S_ISREG(entry.st_mode): 
                filename = entry.filename
                log.info("Retrieving file: {}/{}".format(path,filename))
                sftp.get('{}/{}'.format(path, filename), localpath='/tmp/sftp_file', preserve_mtime=True)
                log.info('Copying file to S3 bucket and path: s3://{}/{}/{}'.format(bucket_name, target_path.lstrip('/'), filename))
                s3_client = boto3.client(service_name='s3')
                s3_client = s3_client.upload_file(Filename='/tmp/sftp_file', Bucket=bucket_name, Key='{}/{}'.format(target_path.lstrip('/'), filename))
                os.remove('/tmp/sftp_file')
            else:
                log.debug('Unmatched: {}. Directory: {}'.format(entry.filename, S_ISDIR(entry.st_mode)))
    
    log.info('Closing connection to SFTP server: {}'.format(sftp_host))
    sftp.close()
    
    
    return True
