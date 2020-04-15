# Cross-sell recommendations for E-commerce

## A project submitted to the AWS Marketplace Developer Challenge
#### website: https://awsmarketplaceml.devpost.com


This project can run locally. It fetches transactional data from any Woocommerce Shop using the Woocommerce Rest API, then moves the data to an S3 bucket. The AWS Sagemaker Batch Transform Job retrieves this data from the S3 bucket and uses it to train a [Mphasis-Mphasis-HyperGraf-Market-Basket-Analysis](https://aws.amazon.com/marketplace/pp/Mphasis-Mphasis-HyperGraf-Market-Basket-Analysis/prodview-y6z3fk7gvudgs) model from the AWS Marketplace.   The model outputs product recommendations based on patterns extracted from previous customer purchases. These recommendations can be used in the online shop for cross-selling purposes.  In order to integrate these recommendations to the online shop, we use the Woocommerce Rest API to upload the recommendations to the MySql database of WordPress.

After running the full notebook, we will have populated the 'cross_sell_ids' field of our MySQL database (which is empty by default).  Woocommerce provides several options to visualize these product recommendations as sliders on Product or Checkout pages.

## Usage 

Create a virtual enviroment using 

    conda create -n cross-seller-env pip
    
Install dependencies with 

    pip install -r requirements.txt
    
Activate the environment 

    conda activate cross-seller-env
    
Create configuration variables file 'configs/config.json', following the template provided (type, example):

```json
{
   "aws_keys":{
      "access_key": (str),
      "secret_key": (str)
   },
   "batch_transform_job":{
      "role_name": (str, "AmazonSageMaker-ExecutionRole-..."),
      "model_package_arn": (str, "arn:aws:sagemaker:eu-central-1:...",
      "instance_type": (str, "ml.m5.large"),
      "instance_count": (int, 1)
   },
   "s3":{
      "region_name": (str, "eu-central-1"),
      "bucket": (str , "mybucket"),
      "input_file": (str, "input_data.csv")
   },
   "woocommerce":{
      "url": (str),
      "consumer_key": (str),
      "consumer_secret": (str)
   }
}       
```


## Running Batch Transform Job

To run a batch transform job you can use the CLI provided

    python update_recommendations.py -i "data/input_data.csv" -o "data/output_data.csv"
    
Alternatively, you can use the jupyter notebook provided 'aws_marketplace_cross_sell_recommendations.ipynb'.  
