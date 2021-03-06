# Cross-sell recommendations for E-commerce

## A project submitted to the AWS Marketplace Developer Challenge
#### website: https://awsmarketplaceml.devpost.com


This project can run locally, it provides a way of automatizing the cross-sell recommendations for small and medium size merchants with a Woocommerce online shop.  It fetches transactional data from any Woocommerce Shop using the Woocommerce Rest API, then moves the data to an S3 bucket. The AWS Sagemaker Batch Transform Job retrieves this data from the S3 bucket and uses it to train a [Mphasis-Mphasis-HyperGraf-Market-Basket-Analysis](https://aws.amazon.com/marketplace/pp/Mphasis-Mphasis-HyperGraf-Market-Basket-Analysis/prodview-y6z3fk7gvudgs) model from the AWS Marketplace.   The model outputs product recommendations based on patterns extracted from previous customer purchases. These recommendations can be used in the online shop for cross-selling purposes.  In order to integrate these recommendations to the online shop, we use the Woocommerce Rest API to upload the recommendations to the MySql database of WordPress.

After running the full notebook, we will have populated the 'cross_sell_ids' field of our MySQL database (which is empty by default).  Woocommerce provides several options to visualize these product recommendations as sliders on Product or Checkout pages.

## Architecture 

![](https://github.com/celis/personal/blob/master/images/architecture.png)

## Usage 

Create a virtual enviroment using 

    conda create -n cross-seller-env pip
    
Activate the environment 

    conda activate cross-seller-env
        
Install dependencies with 

    pip install -r requirements.txt
   
Create configuration variables file 'configs/config.json', following the template provided:

```json
{
   "aws_keys":{
      "access_key": (str),
      "secret_key": (str)
   },
   "batch_transform_job":{
      "role_name": (str),
      "model_package_arn": (str),
      "instance_type": (str),
      "instance_count": (int)
   },
   "s3":{
      "region_name": (str),
      "bucket": (str),
      "input_file": (str)
   },
   "woocommerce":{
      "url": (str),
      "consumer_key": (str),
      "consumer_secret": (str)
   }
}       
```

The repository contains some sample data (in './data/) that can be used for testing purposes:

* flowers_sample_products.csv: sample product inventory used to set up an online shop for the [competition](https://awsmarketplaceml.devpost.com).  Its a small variation around the standard Woocommerce sample product data.

* input_data.csv: Adaptation of the [Mphasis-Mphasis-HyperGraf-Market-Basket-Analysis](https://aws.amazon.com/marketplace/pp/Mphasis-Mphasis-HyperGraf-Market-Basket-Analysis/prodview-y6z3fk7gvudgs) sample input to our online shop.  This file contains artificial orders. 

* output_data.csv: Expected output from the algorithm


## Running Batch Transform Job

To run a batch transform job you can use the CLI provided

    python update_recommendations.py -i "data/input_data.csv" -o "data/output_data.csv"
    
Alternatively, you can use the jupyter notebook provided 'aws_marketplace_cross_sell_recommendations.ipynb'.  
