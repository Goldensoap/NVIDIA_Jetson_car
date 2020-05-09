class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

if __name__ == "__main__":

    getch = _Getch()
    while True:
        ch = getch()
        if ch == bytes('q','ascii') or ch == 'q':
            break
        elif ch == bytes.fromhex('e0'):
            d = getch()
            if d == bytes('H','ascii'):
                print("↑")
            elif d == bytes('P','ascii'):
                print("↓")
            elif d == bytes('K','ascii'):
                print("←")
            elif d == bytes('M','ascii'):
                print("→")
        elif ch == bytes('r','ascii'):
            print("重启视频端口")
        else:
            print(ch)
            print(type(ch))
