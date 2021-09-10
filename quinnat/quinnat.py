import urlock
import time
import datetime
import json

DA_EPOCH = 170141184475152167957503069145530368000
DA_SECOND = 18446744073709551616

def unix_time_to_da():
    time_since_epoch = int((current_epoch() * DA_SECOND) / 1000.0)
    return str.format("/{}", DA_EPOCH + time_since_epoch)

def current_epoch():
    return int(time.time_ns() / 1_000_000.0)

class Quinnat():
    def __init__(self, url, ship_name, code):
        self.url = url
        self.ship_name = ship_name
        self.code = code

    def connect(self):
        self.ship = urlock.Urlock(self.url, self.code)
        self.ship.connect()

    def listen(self, *hooks):
        self.ship.subscribe(self.ship_name, "graph-store", "/updates")

        pipe = self.ship.sse_pipe()

        for event in pipe.events():
            self.ship.ack(int(event.id))
            data = json.loads(event.data)
            if "err" in data:
                print(data["err"])
            elif self.is_node_add(data):
                message = Message.from_add_nodes(data["json"]["graph-update"]["add-nodes"])
                if message.author != self.ship_name:
                    for hook in hooks:
                        hook(message, self.make_replier(message))

    def post_message(self, host_ship, resource_name, *contents):
        node_name = unix_time_to_da()

        poke_obj = {
            "add-nodes": {
                "resource": {
                    "name": resource_name,
                    "ship": "~" + host_ship,
                },
                "nodes": {
                    node_name: {
                        "post": {
                            "index": node_name,
                            "author": "~" + self.ship_name,
                            "time-sent": current_epoch(),
                            "signatures": [],
                            "contents": contents,
                            "hash": None
                        },
                        "children": None
                    }
                }
            }
        }
        self.ship.poke(
            self.ship_name,
            "graph-push-hook",
            "graph-update-2",
            poke_obj
        )

    def make_replier(self, original):
        return lambda *contents: self.post_message(
            original.host_ship, original.resource_name, *contents
        )

    def is_node_add(self, data):
        return ("json" in data) and \
        ("graph-update" in data["json"]) and \
        ("add-nodes" in data["json"]["graph-update"])

class Message():
    def __init__(self, resource_name, host_ship, author, time_sent, contents):
        def element(c):
            if "text" in c:
                return c["text"]
            elif "url" in c:
                return c["url"]
            elif "mention" in c:
                return c["mention"]
            else:
                return ""

        self.resource_name = resource_name
        self.host_ship = host_ship
        self.author = author
        self.time_sent = time_sent
        self.contents = contents
        self.full_text = "\n".join([
            element(c)
            for c
            in self.contents
        ])

    @staticmethod
    def from_add_nodes(update):
        nodes = update["nodes"]
        node_name = list(nodes.keys())[0]
        post = nodes[node_name]["post"]

        return Message(
            update["resource"]["name"],
            update["resource"]["ship"],
            post["author"],
            post["time-sent"],
            post["contents"]
        )
