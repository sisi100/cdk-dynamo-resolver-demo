import aws_cdk as cdk
import aws_cdk.aws_appsync as appsync
import aws_cdk.aws_dynamodb as dynamodb

app = cdk.App()
stack = cdk.Stack(app, "cdk-dynamo-resolver-demo-stack")

api = appsync.GraphqlApi(stack, "Api",
    name="demo",
    schema=appsync.SchemaFile.from_asset("schema.graphql"),
    authorization_config=appsync.AuthorizationConfig(
        default_authorization=appsync.AuthorizationMode(
            authorization_type=appsync.AuthorizationType.IAM
        )
    ),
    xray_enabled=True
)

demo_table = dynamodb.Table(stack, "DemoTable",
    partition_key=dynamodb.Attribute(
        name="id",
        type=dynamodb.AttributeType.STRING
    )
)

demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)

# Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
# Resolver Mapping Template Reference:
# https://docs.aws.amazon.com/appsync/latest/devguide/resolver-mapping-template-reference-dynamodb.html
demo_dS.create_resolver("QueryGetDemosResolver",
    type_name="Query",
    field_name="getDemos",
    request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
    response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
)

# Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
demo_dS.create_resolver("MutationAddDemoResolver",
    type_name="Mutation",
    field_name="addDemo",
    request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
        appsync.PrimaryKey.partition("id").is_("input.id"),
        appsync.Values.projecting("input")),
    response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
)

# To enable DynamoDB read consistency with the `MappingTemplate`:
# demo_dS.create_resolver("QueryGetDemosConsistentResolver",
#     type_name="Query",
#     field_name="getDemosConsistent",
#     request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(True),
#     response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
# )
app.synth()
