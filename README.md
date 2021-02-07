# Quinnat

Quinnat is a library for building urbit chatbots, built with [Urlock](https://github.com/baudtack/urlock-py).

Here's how to use it:

```
#!/usr/bin/python

import quinnat

q = quinnat.Quinnat(
    "http://localhost:8080", # or wherever your ship is running
    "sampel-palnet",
    "your-+code-here",
)

q.connect()

q.post_message("palnet-sampel", "my-chat-1234", {"text": "Hello world!"})

def say_hello(message, replier):
    if "hello bot" in message.full_text:
        replier({"text": "Hello " + message.author})

q.listen(say_hello)
```