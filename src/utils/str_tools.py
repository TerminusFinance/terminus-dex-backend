import codecs


def b64str_to_bytes(b64str):
    b64bytes = codecs.encode(b64str, "utf-8")
    return codecs.decode(b64bytes, "base64")


def b64str_to_hex(b64str):
    _bytes = b64str_to_bytes(b64str)
    _hex = codecs.encode(_bytes, "hex")
    return codecs.decode(_hex, "utf-8")


def bytes_to_b64str(bytes_arr):
    return codecs.decode(codecs.encode(bytes_arr, "base64"), "utf-8").replace("\n", "")
