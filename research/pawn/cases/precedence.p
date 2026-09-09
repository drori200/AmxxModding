#include <lab>
main()
{
    var a = identity(2), b = identity(3), c = identity(4);
    check(a + b * c, 14);
    check((a + b) * c, 20);
    check(c - b - a, -1);
    check(a << 1 + 1, 8);
    check((a | b) & c, 0);
    check(a == 2 && b == 3 || c == 0, true);
    var x, y;
    x = y = 5;
    check(x, 5); check(y, 5);
    x += 3; x *= 2; x /= 4; x %= 3;
    check(x, 1);
    return 0;
}
