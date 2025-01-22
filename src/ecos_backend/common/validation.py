class MaxBodySizeException(Exception):
    def __init__(self, body_len: str) -> None:
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int) -> None:
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes) -> None:
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)
