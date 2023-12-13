def a():
    print("bru")

def b(text):
    print(text)

tests = {
    "first": a,
    "second": b
}

tests["first"]()