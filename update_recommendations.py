from src.configuration import Configuration
from src.services import S3, Woocommerce
import logging
import os
import argparse
import boto3
from sagemaker import ModelPackage
import sagemaker as sagemaker


def cli():
    """
    Simply run this script with '--help' to see all options.
    """
    desc = "Pipeline to train a AWS Marketplace model on Woocommerce data and upload cross-sell product recommendations"

    logging.basicConfig(
        format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
    )

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-i", "--input", help="input path", dest="input", required=True)

    parser.add_argument(
        "-o", "--output", help="output_path", dest="output", required=True
    )

    args = parser.parse_args()

    logging.info("configure services")
    config = Configuration("configs/config.json").parameters

    s3 = S3(
        region_name=config["s3"]["region_name"],
        access_key=config["aws_keys"]["access_key"],
        secret_key=config["aws_keys"]["secret_key"],
        bucket=config["s3"]["bucket"],
    )

    woocommerce = Woocommerce(
        url=config["woocommerce"]["url"],
        consumer_key=config["woocommerce"]["consumer_key"],
        consumer_secret=config["woocommerce"]["consumer_secret"],
    )

    logging.info("download data from Woocommerce")
    woocommerce.download_data(args.input)

    logging.info("upload data to S3")
    s3.upload(args.input, "input_data.csv")

    logging.info("configure Batch Transform Job")
    model_package_arn = config["batch_transform_job"]["model_package_arn"]

    iam = boto3.client("iam")
    role = iam.get_role(RoleName=config["batch_transform_job"]["role_name"])["Role"][
        "Arn"
    ]

    sagemaker_session = sagemaker.Session()

    model = ModelPackage(
        model_package_arn=model_package_arn,
        role=role,
        sagemaker_session=sagemaker_session,
    )

    output_path = "s3://" + os.path.join(config["s3"]["bucket"], "output")

    transformer = model.transformer(
        instance_count=config["batch_transform_job"]["instance_count"],
        instance_type=config["batch_transform_job"]["instance_type"],
        output_path=output_path,
    )

    input_path = "s3://" + os.path.join(
        config["s3"]["bucket"], config["s3"]["input_file"]
    )

    transformer.transform(input_path, content_type="text/csv")

    logging.info('batch transform job starting')
    transformer.wait()

    logging.info("downloading recommendations from S3")
    bucket_folder = transformer.output_path.rsplit("/")[3]
    key = os.path.join(
        bucket_folder, config["s3"]["input_file"].split("/")[-1] + ".out"
    )

    s3.download(key, args.output)

    logging.info("Push recommendations to Woocommerce")
    woocommerce.upload_recommendations(args.output)


if __name__ == "__main__":

    cli()
