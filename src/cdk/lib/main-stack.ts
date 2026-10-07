import * as path from "path";
import { NodejsBuild } from "deploy-time-build";
import { aws_iam as iam } from "aws-cdk-lib";
import * as cdk from "aws-cdk-lib";
import {
  CloudFrontToS3,
  CloudFrontToS3Props,
} from "@aws-solutions-constructs/aws-cloudfront-s3";
import {
  aws_s3 as s3,
  aws_s3_deployment as s3deploy,
  aws_cloudfront as cloudfront,
  aws_cloudfront_origins as origins,
  aws_wafv2 as wafv2,
  aws_certificatemanager as acm,
} from "aws-cdk-lib";
import { Construct } from "constructs";

export class MainStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Import existing certificate
    const certificate = acm.Certificate.fromCertificateArn(
      this,
      "CustomCertificate",
      "arn:aws:acm:us-east-1:089126623187:certificate/f5c3b6dc-6cb4-45f5-9a36-5ff633ea3899"
    );

    const commonBucketProps: s3.BucketProps = {
      autoDeleteObjects: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      objectOwnership: s3.ObjectOwnership.OBJECT_WRITER,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    };

    const cloudFrontToS3Props: CloudFrontToS3Props = {
      insertHttpSecurityHeaders: false,
      loggingBucketProps: commonBucketProps,
      bucketProps: commonBucketProps,
      cloudFrontLoggingBucketProps: commonBucketProps,
      cloudFrontLoggingBucketAccessLogBucketProps: commonBucketProps,
      cloudFrontDistributionProps: {
        errorResponses: [
          {
            httpStatus: 403,
            responseHttpStatus: 200,
            responsePagePath: "/index.html",
          },
          {
            httpStatus: 404,
            responseHttpStatus: 200,
            responsePagePath: "/index.html",
          },
        ],
        // webAclId: geoMatchWebAcl.attrArn,
        certificate: certificate,
        // domainNames: ["respell.ocooltech.com"],
      },
    };

    const { cloudFrontWebDistribution, s3Bucket } = new CloudFrontToS3(
      this,
      "CloudFrontToS3",
      cloudFrontToS3Props
    );

    // Build and deploy website
    const build = new NodejsBuild(this, "BuildWebsite", {
      assets: [
        {
          path: "../",
          exclude: [
            ".git",
            ".gitignore",
            "*.md",
            "node_modules",
            "dist",
            ".vite",
            ".githooks",
            "deploy",
          ],
        },
      ],
      destinationBucket: s3Bucket!,
      // memoryLimit=1024,  // Increase from default 128MB to 1024MB
      // timeout=Duration.minutes(15)  // Increase timeout from default 5 minutes
      distribution: cloudFrontWebDistribution!,
      outputSourceDirectory: "./src/web/dist",
      buildCommands: [
        "npm ci",
        "npm run build -- --debug",
        "ls -la ./src/web/dist",
      ],
      nodejsVersion: 20,
      buildEnvironment: {
        NODE_OPTIONS: "--max-old-space-size=4096",
      },
    });

    // Add explicit IAM permissions to ensure the Lambda function can start CodeBuild
    const customResourceHandler = build.node.findChild('CustomResourceHandler') as any;
    if (customResourceHandler && customResourceHandler.role) {
      customResourceHandler.role.addToPrincipalPolicy(new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['codebuild:StartBuild', 'codebuild:BatchGetBuilds'],
        resources: ['*'], // We need wildcard since the project ARN is created dynamically
      }));
    }
  }
}

export default MainStack;
