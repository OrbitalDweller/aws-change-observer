from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
)
from constructs import Construct


class AwsChangeObserverStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Constants
        TABLE_NAME = 'LocationMarkers'
        FUNCTION_NAME = 'getMarkersRequest'
        GET_MARKERS_REQUEST_LAMBDA_CODE_PATH = 'lambdas/get_markers_request'

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

        # Define the Lambda Layer for data_service
        data_service_layer = aws_lambda.LayerVersion(
            self, 'DataServiceLayer',
            code=aws_lambda.Code.from_asset("layers/data_service_layer"),  # Path to the directory, NOT .zip
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8, aws_lambda.Runtime.PYTHON_3_9],
            description="A layer containing the data_service module"
        )

        # Define the Lambda Layer for coordinate
        coordinate_layer = aws_lambda.LayerVersion(
            self, 'CoordinateLayer',
            code=aws_lambda.Code.from_asset("layers/coordinate_layer"), 
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_8],
            description="A layer containing the coordinate module"
        )

        # Lambda function
        get_markers_request_lambda = aws_lambda.Function(
            self, 'GetMarkersRequestFunction',
            function_name=FUNCTION_NAME,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="get_markers_request_lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(GET_MARKERS_REQUEST_LAMBDA_CODE_PATH),
            layers=[data_service_layer],
            environment={
                'TABLE_NAME': table.table_name,
            },
        )

        # Grant the Lambda function read access to the DynamoDB table
        table.grant_read_data(get_markers_request_lambda)

        # API Gateway
        api = apigateway.RestApi(
            self, 'ChangeObserverAPI',
            rest_api_name='ChangeObserverAPI',
        )

        # Add a specific resource
        markers_resource = api.root.add_resource("markers")

        # Create Lambda integration
        get_markers_integration = apigateway.LambdaIntegration(get_markers_request_lambda)

        # Add GET method with Lambda integration
        markers_resource.add_method("GET", get_markers_integration)  # GET /markers

        markers_resource.add_cors_preflight(
             allow_origins=apigateway.Cors.ALL_ORIGINS,
             allow_methods=["GET", "OPTIONS"],
        )
