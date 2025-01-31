import enum
import typing
import magic

from streaming_form_data.targets import BaseTarget
from streaming_form_data.validators import MaxSizeValidator


class FileType(enum.Enum):
    JPG = ".jpg"
    PNG = ".png"


class MaxBodySizeException(Exception):
    def __init__(self, body_len: str) -> None:
        self.body_len: str = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int) -> None:
        self.body_len: int = 0
        self.max_size: int = max_size

    def __call__(self, chunk: bytes) -> None:
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)


class InvalidFileTypeException(Exception):
    def __init__(self, detail: str) -> None:
        self.detail: str = detail


class FileTypeValidator:
    ALLOWED_MIME_TYPES: dict[str, str] = {
        "image/jpeg": FileType.JPG.value,
        "image/png": FileType.PNG.value,
    }

    @staticmethod
    def validate(file_bytes: bytes) -> str:
        mime = magic.Magic(mime=True)
        file_type: str = mime.from_buffer(file_bytes)

        if file_type not in FileTypeValidator.ALLOWED_MIME_TYPES:
            raise InvalidFileTypeException(
                detail=f"Invalid file type: {file_type}. Only .jpg and .png are allowed."
            )

        return FileTypeValidator.ALLOWED_MIME_TYPES[file_type]


class BytesTarget(BaseTarget):
    """Custom target to store file content in bytes instead of saving to disk."""

    def __init__(self, validator: typing.Optional[MaxSizeValidator] = None) -> None:
        super().__init__()
        self._data = bytearray()
        self.validator: MaxSizeValidator | None = validator

    def on_data_received(self, chunk: bytes) -> None:
        """Appends received chunks to the bytearray."""
        if self.validator:
            self.validator(chunk)
        self._data.extend(chunk)

    @property
    def content(self) -> bytes:
        """Returns the file content as bytes."""
        return bytes(self._data)
