# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


from twisted.internet import reactor, protocol

METHODS_ENUM = {
    "GET": "GET",
    "POST": "POST",
    "DELETE": "DELETE",
    "PUT": "PUT",
}

STATUS_CODE_ENUM = {
    "OK": "HTTP/1.1 200 OK",
    "NotFound": "HTTP/1.1 404 Not Found",
    "Created": "HTTP/1.1 201 Created",
}    

class Headers:
    def __init__(self):
        self.dict = {}
    
    def add(self, k, v):
        self.dict[k] = v
    
    def get(self, k):
        return self.dict[k] if k in self.dict else None
    
    def getAll(self):
        return self.dict

class HttpRequest:
    def __init__(self, request: bytes):
        # binary raw request
        self.request = request

    def decode(self):
        decoded = self.request.decode(encoding="ascii")

        decoded_list = decoded.split("\r\n")

        # go through request line
        req_line_list = decoded_list[0].split(' ')

        self.method = req_line_list[0]
        if self.method not in METHODS_ENUM:
            raise ValueError("Incorrect method")
        
        self.target = req_line_list[1]
        self.http_type = req_line_list[2]

        # decode header
        self.headers = Headers()
        for line in decoded_list[1:-1]:
            if line:
                i = line.index(': ')
                k, v = line[:i], line[i+2:]
                self.headers.add(k, v)    

        # decode body
        self.body = req_line_list[-1]

class HttpResponse:
    def __init__(self, status_code: str, headers: Headers, content: str | bytes):
        self.status_code = status_code
        self.headers = headers
        self.content = content

    def get_bytes(self) -> bytes:
        arr = []

        # add status code
        arr.append(f"{self.status_code}\r\n")

        # add headers
        for k, v in self.headers.getAll().items():
            arr.append(f"{k}: {v}\r\n")
        arr.append("\r\n")

        # add body if it's string, if bytes handle later
        if type(self.content) == str:
            arr.append(self.content)
        
        # convert to array of bytes
        encoded_bytes = "".join(arr).encode(encoding="utf-8")

        if type(self.content) == bytes:
            encoded_bytes += self.content
        
        return encoded_bytes

class Echo2(protocol.Protocol):
    """This is just about the simplest possible protocol"""
    
    def dataReceived(self, data):
        "TCP Method"
        req = HttpRequest(data)
        req.decode()

        print(data)

        header = Headers()
        header.add("Content-Type", "text/html")
        if req.headers.getAll()['User-Agent']:
            header.add("Content-Length", len(req.headers.getAll()['User-Agent']))
            content = req.headers.getAll()['User-Agent']

        resp = HttpResponse(status_code=STATUS_CODE_ENUM["OK"], headers=header, content=content)

        self.transport.write(resp.get_bytes())


def main():
    """This runs the protocol on port 8001"""
    factory = protocol.ServerFactory()
    factory.protocol = Echo2
    reactor.listenTCP(8001,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()

"""
POST content - String

response return content as bytes
applications/octect-streams
"""