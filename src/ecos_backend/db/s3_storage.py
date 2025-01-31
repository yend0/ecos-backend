import io
import pathlib
import typing

import boto3
import botocore

from ecos_backend.common import config


class Boto3DAO:
    def __init__(
        self,
        bucket_name: str,
        endpoint: str,
        access_key: str,
        secret_key: str,
    ) -> None:
        self._bucket_name: str = bucket_name
        self._endpoint: str = endpoint
        self._access_key: str = access_key
        self._secret_key: str = secret_key

    def _create_s3_client(self) -> boto3.client:
        client = boto3.client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            config=botocore.client.Config(signature_version="s3v4"),
        )
        return client

    def upload_object(
        self,
        prefix: str,
        source_file_name: str,
        content: str | bytes,
    ) -> typing.Any:
        client = self._create_s3_client()
        destination_path = str(pathlib.Path(prefix, source_file_name))

        if isinstance(content, bytes):
            buffer = io.BytesIO(content)
        else:
            buffer = io.BytesIO(content.encode("utf-8"))
        client.upload_fileobj(buffer, self._bucket_name, destination_path)

        url = client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": f"{self._bucket_name}",
                "Key": f"{destination_path}",
            },
            ExpiresIn=3600,
        )
        return url

    def get_objects(self, prefix: str) -> list[str]:
        client = self._create_s3_client()
        response = client.list_objects_v2(Bucket=self._bucket_name, Prefix=prefix)
        storage_content: list[str] = []

        try:
            contents = response["Contents"]
        except KeyError:
            return storage_content

        for item in contents:
            storage_content.append(item["Key"])

        return storage_content

    def delete_object(self, prefix: str, source_file_name: str) -> None:
        client = self._create_s3_client()
        path_to_file = str(pathlib.Path(prefix, source_file_name))
        client.delete_object(Bucket=self._bucket_name, Key=path_to_file)

    def __call__(self) -> "Boto3DAO":
        """Allows the class instance to be used as a dependency."""
        return self


def s3_bucket_factory(config: config.S3Config) -> Boto3DAO:
    return Boto3DAO(
        bucket_name=config.BUCKET_NAME,
        endpoint=config.ENDPOINT,
        access_key=config.ACCESS_KEY,
        secret_key=config.SECRET_KEY,
    )
