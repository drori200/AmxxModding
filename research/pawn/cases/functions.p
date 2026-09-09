#include <lab>
#include <core>
sum(const values[], count = sizeof values, scale = 2)
{
    var total;
    for (var i = 0; i < count; i++) total += values[i];
    return total * scale;
}
factorial(n) { return n <= 1 ? 1 : n * factorial(n - 1); }
bump(&value) { return ++value; }
main()
{
    var values[] = [1, 2, 3], value = 5;
    check(sum(values), 12);
    check(sum(values, .scale = 3), 18);
    check(sum(values, 2, 1), 3);
    check(factorial(5), 120);
    check(bump(value), 6); check(value, 6);
    return 0;
}
