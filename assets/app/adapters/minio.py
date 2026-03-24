import json
from io import BytesIO

from minio import Minio, S3Error

from app.configs.minio import MinioConfig
from app.core.models import AvatarID
from app.core.storage import Storage


class MinioStorage(Storage):
    def __init__(self, config: MinioConfig):
        self.client = Minio(
            f"{config.host}:{config.port}",
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=False,
        )

        if not self.client.bucket_exists("avatars"):
            self.client.make_bucket("avatars")
        self.client.set_bucket_policy(
            "avatars",
            json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                            "Resource": ["arn:aws:s3:::avatars"],
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": ["arn:aws:s3:::avatars/*"],
                        },
                    ],
                }
            ),
        )

    async def save_avatar(self, id: AvatarID, data: bytes):
        self.client.put_object("avatars", str(id), BytesIO(data), len(data))

    async def avatar_exists(self, id: AvatarID) -> bool:
        try:
            _ = self.client.stat_object("avatars", str(id))
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            raise e
