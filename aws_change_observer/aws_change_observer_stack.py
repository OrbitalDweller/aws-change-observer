from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_events as events,
    aws_events_targets as event_targets,
    Duration,
    aws_s3 as s3
)
from constructs import Construct


class AwsChangeObserverStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, is_prod: bool = False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Constants
        DOMAIN_NAME = 'change-observer.com'
        SUBDOMAIN = 'api'
        TABLE_NAME = 'LocationMarkers'        
        GET_MARKERS_REQUEST_LAMBDA_CODE_PATH = 'lambdas/get_markers_request'
        GET_MARKER_REQUEST_LAMBDA_CODE_PATH = 'lambdas/get_marker_request'
        ADD_MARKER_REQUEST_LAMBDA_CODE_PATH = 'lambdas/add_marker_request'
        DELETE_MARKER_REQUEST_LAMBDA_CODE_PATH = 'lambdas/delete_marker_request'
        UPDATE_MARKER_REQUEST_LAMBDA_CODE_PATH = 'lambdas/update_marker_request'
        OBSERVE_LAMBDA_CODE_PATH = 'lambdas/observe'

        # Create the DynamoDB table
        table = dynamodb.Table(
            self, 'LocationMarkersTable',
            table_name=TABLE_NAME,
            partition_key=dynamodb.Attribute(
                name='markerId',
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,  # Use RETAIN in production
        )

        # Create the S3 bucket
        image_bucket = s3.Bucket(
            self, 'ObservationBucket',
            removal_policy=RemovalPolicy.DESTROY,  # Use RETAIN in production
            auto_delete_objects=True,              # Deletes objects when the bucket is deleted
            public_read_access=True,                # Makes all objects publicly readable
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,  # Allow public ACLs
                block_public_policy=False,  # Allow public bucket policies
                ignore_public_acls=False,  # Do not ignore public ACLs
                restrict_public_buckets=False  # Do not restrict public buckets
        )
        )

        # Define the Lambda Layer for shared classes
        shared_classes_layer = aws_lambda.LayerVersion(
            self, 'SharedClassesLayer',
            code=aws_lambda.Code.from_asset("layers/shared_classes_layer"), 
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8],
            description="A layer containing the shared classes module"
        )

        # Basic lambda role
        lambda_role_basic = iam.Role(
            self, 'LambdaRoleBasic',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            ]
        )

        # Lambda function for adding a markers
        add_marker_request_lambda = aws_lambda.Function(
            self, 'AddMarkerRequestFunction',
            function_name='addMarkerRequest',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="add_marker_request_lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(ADD_MARKER_REQUEST_LAMBDA_CODE_PATH),
            layers=[shared_classes_layer],
            role=lambda_role_basic,
            environment={
                'TABLE_NAME': table.table_name,
            },
        )

        # Lambda function for getting all markers
        get_markers_request_lambda = aws_lambda.Function(
            self, 'GetMarkersRequestFunction',
            function_name='getMarkersRequest',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="get_markers_request_lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(GET_MARKERS_REQUEST_LAMBDA_CODE_PATH),
            layers=[shared_classes_layer],
            role=lambda_role_basic,
            environment={
                'TABLE_NAME': table.table_name,
            },
        )

        # Lambda function for getting a marker by markerId
        get_marker_request_lambda = aws_lambda.Function(
            self, 'GetMarkerRequestFunction',
            function_name='getMarkerRequest',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="get_marker_request_lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(GET_MARKER_REQUEST_LAMBDA_CODE_PATH),
            layers=[shared_classes_layer],
            role=lambda_role_basic,
            environment={
                'TABLE_NAME': table.table_name,
            },
        )

        # Lambda function for updating a marker
        update_marker_request_lambda = aws_lambda.Function(
            self, 'UpdateMarkerRequestFunction',
            function_name='updateMarkerRequest',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="update_marker_request_lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(UPDATE_MARKER_REQUEST_LAMBDA_CODE_PATH),
            layers=[shared_classes_layer],
            role=lambda_role_basic,
            environment={
                'TABLE_NAME': table.table_name
            },
        )

        # Lambda function for deleting a marker
        delete_marker_request_lambda = aws_lambda.Function(
            self, 'DeleteMarkerRequestFunction',
            function_name='deleteMarkerRequest',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="delete_marker_request_lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(DELETE_MARKER_REQUEST_LAMBDA_CODE_PATH),
            layers=[shared_classes_layer],
            role=lambda_role_basic,
            environment={
                'TABLE_NAME': table.table_name
            },
        )

        # Lambda role for observation
        lambda_role_observe = iam.Role(
            self, 'LambdaRoleObserve',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonRekognitionFullAccess') 
            ]
        )

        # Lambda function for change observation
        observe_lambda = aws_lambda.Function(
            self, 'ObserveFunction',
            function_name='Observe',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="observe_lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(OBSERVE_LAMBDA_CODE_PATH),
            layers=[shared_classes_layer],
            role=lambda_role_observe,
            timeout=Duration.minutes(10), # may need more time
            memory_size=256, # may need more memory 
            environment={
                'TABLE_NAME': table.table_name,
                'BUCKET_NAME': image_bucket.bucket_name,
            },
        )

        daily_rule = events.Rule(
            self, 'DailyRule',
            schedule=events.Schedule.cron(minute='0', hour='0'),  # Triggers at 00:00 UTC daily
        )

        daily_rule.add_target(event_targets.LambdaFunction(observe_lambda))

        # Grant access to the DynamoDB table
        table.grant_read_data(get_markers_request_lambda)
        table.grant_read_data(get_marker_request_lambda)
        table.grant_read_data(update_marker_request_lambda)
        table.grant_write_data(add_marker_request_lambda)
        table.grant_write_data(update_marker_request_lambda)
        table.grant_write_data(delete_marker_request_lambda)
        table.grant_read_data(observe_lambda)
        table.grant_write_data(observe_lambda)

        # Grant access to the S3 bucket
        image_bucket.grant_read_write(observe_lambda)

        # API Gateway
        api = apigateway.RestApi(
            self, 'ChangeObserverAPI',
            rest_api_name='ChangeObserverAPI',
        )

        # Add a specific resource
        markers_resource = api.root.add_resource("markers")

        # Add GET method for getting markers
        get_markers_integration = apigateway.LambdaIntegration(get_markers_request_lambda)
        markers_resource.add_method("GET", get_markers_integration)

        markers_resource.add_cors_preflight(
             allow_origins=apigateway.Cors.ALL_ORIGINS,
             allow_methods=["GET", "OPTIONS"],
        )

        # Add a specific resource
        marker_resource = api.root.add_resource("marker")
                
        # Add GET method for getting a marker by markerId
        get_marker_integration = apigateway.LambdaIntegration(get_marker_request_lambda)
        marker_resource.add_method("GET", get_marker_integration)

        # Add POST method for adding a marker
        add_marker_integration = apigateway.LambdaIntegration(add_marker_request_lambda)
        marker_resource.add_method("POST", add_marker_integration)

        # Add PUT method for updating a marker
        update_marker_integration = apigateway.LambdaIntegration(update_marker_request_lambda)
        marker_resource.add_method("PUT", update_marker_integration)

        # Add DELETE method for deleting a marker
        delete_marker_integration = apigateway.LambdaIntegration(delete_marker_request_lambda)
        marker_resource.add_method("DELETE", delete_marker_integration)
        
        marker_resource.add_cors_preflight(
            allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        )

        if is_prod:
            # Route 53 Hosted Zone
            hosted_zone = route53.HostedZone.from_lookup(self, "ChangeObserverHostedZone", domain_name=DOMAIN_NAME)

            # SSL Certificate in ACM
            certificate = acm.Certificate(
                self, "ChangeObserverAPICertificate",
                domain_name=f"{SUBDOMAIN}.{DOMAIN_NAME}",
                validation=acm.CertificateValidation.from_dns(hosted_zone)
            )

            # Custom Domain for API Gateway
            custom_domain = apigateway.DomainName(
                self, "ChangeObserverAPICustomDomain",
                domain_name=f"{SUBDOMAIN}.{DOMAIN_NAME}",
                certificate=certificate
            )

            # Map Custom Domain to API Gateway Stage
            apigateway.BasePathMapping(
                self, "BasePathMapping",
                domain_name=custom_domain,
                rest_api=api
            )

            # Route 53 Alias Record to Custom Domain
            route53.ARecord(
                self, "ChangeObserverAPIAliasRecord",
                zone=hosted_zone,
                record_name=SUBDOMAIN,
                target=route53.RecordTarget.from_alias(targets.ApiGatewayDomain(custom_domain))
            )

