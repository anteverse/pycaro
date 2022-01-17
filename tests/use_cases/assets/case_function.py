from pathlib import Path


def do_something(arg1):

    variable = "hello"
    print(arg1)

    print(Path(arg1).as_posix())

    as_posix = Path(arg1).as_posix()

    print(var1)
    print(var2)
    return True


if __name__ == '__main__':
    var1 = 1
    var2 = 2
    do_something("hi")
