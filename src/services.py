import boto3
from woocommerce import API
import pandas as pd


class S3:
    """
    Class responsible for downloading (and uploading) objects from S3 (to S3).
    """

    def __init__(self, region_name, access_key, secret_key, bucket):
        self.region_name = region_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket

    def _boto3_client(self):
        """
        creates a boto3 client instance
        """
        boto3_client = boto3.client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
        return boto3_client

    def download(self, key: str, filename: str):
        """
        Downloads file from S3

        key: The name of the key to download from.
        filename: The path to the file to download to.
        """
        boto3_client = self._boto3_client()
        boto3_client.download_file(self.bucket, key, filename)

    def upload(self, filename: str, key: str):
        """
        Uploads file to S3

        filename: The path to the file to upload.
        key: The name of the key to upload to.
        """
        boto3_client = self._boto3_client()
        boto3_client.upload_file(filename, self.bucket, key)


class Woocommerce:
    """
    Small wrapper around the Woocommerce API responsible for getting the data required for the ML algorithm
    and uploading the cross-sell recommendations
    """

    VERSION = "wc/v3"

    def __init__(self, url: str, consumer_key: str, consumer_secret: str):
        self.url = url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self._api = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            timeout = 10,
            version=self.VERSION,
        )

    def download_data(self, path: str):
        orders_df = self._get_orders()
        products_df = self._get_products()

        orders_df = pd.merge(orders_df, products_df, on="SKUID")
        orders_df = orders_df.sort_values(by="InvoiceID", ascending=True)

        orders_df['InvoiceID'] = orders_df['InvoiceID'].astype(str)
        orders_df['SKUID'] = orders_df['SKUID'].astype(str)

        orders_df.to_csv(path, index=False, encoding='utf-8')

    def upload_recommendations(self, path, top_n: 10):
        recommendations_df = pd.read_csv(path)

        products_df = self._get_products()
        product_mapping = dict(zip(products_df["Item"], products_df["SKUID"]))

        recommendations_df["Item in cart"] = recommendations_df["Item in cart"].map(
            product_mapping
        )
        recommendations_df["Recommendation"] = recommendations_df["Recommendation"].map(
            product_mapping
        )

        recommendations_df = recommendations_df.sort_values(
            by=["Item in cart", "Support"], ascending=False
        )
        recommendations_df = recommendations_df.groupby("Item in cart").head(top_n)
        recommendations_df = (
            recommendations_df.groupby("Item in cart")["Recommendation"]
            .apply(list)
            .reset_index()
        )

        for _, row in recommendations_df.iterrows():
            data = {"cross_sell_ids": row["Recommendation"]}
            self._api.put(f"products/{row['Item in cart']}", data).json()

    def _get_products(self) -> pd.DataFrame:
        page = 1
        response = self._api.get(
            "products", params={"per_page": 100, "page": page}
        ).json()
        products = response.copy()

        while response:
            page += 1
            response = self._api.get(
                "products", params={"per_page": 100, "page": page}
            ).json()
            products += response

        products = [
            {"SKUID": product["id"], "Item": product["name"].upper()} for product in products
        ]
        products_df = pd.DataFrame(products)
        return products_df

    def _get_orders(self) -> pd.DataFrame:
        page = 1
        response = self._api.get("orders", params={"per_page": 100, "page": page}).json()
        orders = response.copy()

        while response:
            page += 1
            response = self._api.get(
                "orders", params={"per_page": 100, "page": page}
            ).json()
            orders += response

        orders = [
            {
                "InvoiceID": order["id"],
                "SKUID": list({item["product_id"] for item in order["line_items"]}),
            }
            for order in orders
        ]
        orders_df = pd.DataFrame(orders)
        orders_df = orders_df.explode("SKUID")
        return orders_df
