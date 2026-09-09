#include <lab>
// Validation must exist when assertions are disabled. Never dereference first.
bool:read_value(const values[], count, index, &result)
{
    if (index < 0 || index >= count) return false;
    result = values[index];
    return true;
}
main()
{
    var values[] = [10, 20, 30], result = 99;
    check(read_value(values, sizeof values, -1, result), false);
    check(result, 99);
    check(read_value(values, sizeof values, 3, result), false);
    check(result, 99);
    check(read_value(values, sizeof values, 0, result), true);
    check(result, 10);
    check(read_value(values, sizeof values, 2, result), true);
    check(result, 30);
    return 0;
}
