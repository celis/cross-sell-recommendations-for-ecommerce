from src.configuration import Configuration
from src.services import S3, Woocommerce


if __name__ == "__main__":

    config = Configuration("configs/config.json").parameters

    s3 = S3()

    woocommerce = Woocommerce()
