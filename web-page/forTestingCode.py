res_body = {
    "created": 1538482340270,
    "modified": 1538485409417,
    "name": "giftest",
    "objects": {
        "BT-42/mp4": {
            "complete": True,
            "contentLength": 20095347,
            "created": 1538482340580,
            "eTag": "s0trPbxdkjlcfYFymXtAsQ==-1",
            "metaData": {},
            "modified": 1538482342946,
            "name": "BT-42.mp4",
            "partMD5s": {
                "BT-42/mp4/part00001": "BMnoqv4Suj3MmnM3gDmMBw=="
            }
        },
        "proto/gif": {
            "complete": True,
            "contentLength": 24652630,
            "created": 1538485406603,
            "eTag": "/dOGDb0KIp9UhRi5UrRjdw==-1",
            "metaData": {},
            "modified": 1538485409417,
            "name": "proto.gif",
            "partMD5s": {
                "proto/gif/part00001": "lN9IhcdbCrxVFuxt/XNUbQ=="
            }
        }
    }
}

VIDEO_EXTENSION = ["mp4", "mov", "avi"]

result = []
for key in res_body["objects"]:
    obj = res_body["objects"][key]["name"]
    filename, extension = obj.rsplit('.', 1)
    if extension.lower() in VIDEO_EXTENSION:
        result.append(obj)


print(result)

