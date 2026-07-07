import zlib, pickle, io, sys

path = sys.argv[1]
needle = sys.argv[2].encode() if len(sys.argv) > 2 else None

raw = open(path, "rb").read()
print("first bytes:", raw[:4].hex())

if raw[:1] == b"\x78":            # zlib stream (78 9c / 78 da / 78 01)
    raw = zlib.decompress(raw)
    print("zlib-compressed, decompressed to", len(raw), "bytes")
else:
    print("raw pickle,", len(raw), "bytes")

if needle:
    print("stale name present:", needle in raw)

class _Stub:
    def __init__(self, *a, **k): pass
    def __setstate__(self, s):
        if isinstance(s, dict): self.__dict__.update(s)

class Tolerant(pickle.Unpickler):
    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except Exception:
            return type(name, (_Stub,), {})   # stub Olex2-internal classes

obj = Tolerant(io.BytesIO(raw)).load()
print("top-level type:", type(obj).__name__)
if isinstance(obj, dict):
    for k, v in obj.items():
        print(f"  {k!r}: {type(v).__name__}")