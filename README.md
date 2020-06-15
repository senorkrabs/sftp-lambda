# sftp-lambda

A SAM application that uses AWS Lambda and Cloudwatch Scheduled Events to transfer files from an SFTP server and copy them to S3.

The Lambda is written in Python and uses pysftp to interface with SFTP servers

## Features
- Transfer multiple files from SFTP to S3 buckets in a single invocation
- File pattern matching. Example: Copy all files matching `/sourcedir/*.csv`

    Note: folder matching and recursive folder matching is not currently supported.
    
- Send files to different bucket paths. For example: Send `/sourcedir/*.csv` to `target-bucket\CSVs` and `/sourcedir/transactions_*.parquet` to `target-bucket\transactions` in a single invocation.


## Limits
We are bound by the limits of Lambda in our requests:
- Max single file size: Approximately 500MB (the storage available in `/tmp`)
- Max runtime: 15 minutes
 
## Components

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- **sftp-lambda/** - Code for the application's Lambda function. 
    -  **app.py** - The Lambda function code.
    -  **requirements.txt** - Python package dependencies that are packaged and deployed with the Lambda
- **template.yaml** - A template that defines the application's AWS resources and deployment parameters. The CloudWatch Scheduled Event and cron expression are defined here.


The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

If you prefer to use an integrated development environment (IDE) to build and test your application, you can use the AWS Toolkit.  
The AWS Toolkit is an open source plug-in for popular IDEs that uses the SAM CLI to build and deploy serverless applications on AWS. The AWS Toolkit also adds a simplified step-through debugging experience for Lambda function code. See the following links to get started.

* [PyCharm](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [IntelliJ](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)
* [Visual Studio](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/welcome.html)

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **BucketName**: The name of the S3 bucket the SFTP files will be copied to
* **SftpHost**: The SFTP host address.
* **SftpUser**: The username that will be used to log into the SFTP server
* **SftpPassword**: The SFTP Password or private key used to log into the server.

    | Important|
    |:-|
    | The password will be securely stored in AWS Secrets Manager and retrieved at runtime. If using a private key, you may need to enter a dummy password and then manually edit the AWS Secrets Manager secret with key because of limitations in the SAM CLI. |
* **SftpPrivateKeyAuth**: Set to `True` if using a private key instead of a password. Default is `False`
* **FilesListJSON**: The JSON string that contains details on the source files and target paths in S3. See example below.
* **VPC**: The ID of VPC that the Lambda should execute in. 
* **Subnets**: A comma-separated list of subnet IDs the Lambda should execute in. These **must** be in the VPC specified by the VPC parameter.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. Must be **yes** to allow IAM role creation for this application. 
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

### FilesListJSON Format
The FilesListJSON parameter is a JSON-formatted array of objects that uses the following format to define what files will be copied to S3:
```
[{"SourceFile": "/my-sftp-directory/subfolder1/*.csv", "TargetPath": "/target-s3-path/subfolder"}, {"SourceFile": "/my-sftp-directory/subfolder2/my-file.parquet", "TargetPath": "/target-s3-path/another-folder"}, {"SourceFile": "/my-sftp-directory/subfolder2/transactions_*.csv", "TargetPath": "/target-s3-path/transactions"}]
```
**SourceFile**: The source directory path and file name on the SFTP server. Supports file pattern matching. Directory/folder pattern matching and recursive path matching is not currently supported.
**TargetPath**: The target patch in the S3 bucket where any matching files will be copied to.

In the example above:
1. Files matching `/my-sftp-directory/subfolder1/*.csv` will be copied to `/target-s3-path/subfolder` in the S3 bucket
2. The file `/my-sftp-directory/subfolder2/my-file.parquet` will be copied to `/target-s3-path/another-folder` in the S3 bucket
3. Files matching `/my-sftp-directory/subfolder2/transactions_*.csv` will be copied to `/target-s3-path/transactions` in S3

You can specify the same `TargetPath` for multiple `SourceFile` items. If there are conflicts, the last file written always wins, overwriting anything from previous items in the list.


## Customization
Once deployed, you could re-use this Lambda with other CloudWatch Events, or even invoke with a Lambda API. A sample of the event structure that the sftp-lambda function expects is located in `events/event.json`

The Lambda could be invoked from resources outside of this SAM app, or you could write them into the app by modifying template.yaml.


## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name <sftp-lambda-stack-name>
```

## Resources

 [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) 
 [pysftp API documentation](https://pysftp.readthedocs.io/en/release_0.2.8/index.html)
 

