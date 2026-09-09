#include <lab>
// Explicit result tag; the parameter tags do not declare the result tag.
Fixed:operator+(Fixed:left, Fixed:right)
{
    return Fixed:(_:left + _:right);
}
consume(Fixed:value) { return _:value; }
main()
{
    var Fixed:left = Fixed:identity(12), Fixed:right = Fixed:identity(30);
    var Fixed:result = left + right;
    check(consume(result), 42);
    return 0;
}
