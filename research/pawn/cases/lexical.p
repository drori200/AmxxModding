#include <lab>
main()
{
    var _Score = 4 // line comment terminates before the next declaration
    var _score = 8
    var value = 1 /* comments separate tokens */ + 2;
    check(_Score, 4); check(_score, 8); check(value, 3);
    check(012, 12); check(12'345, 12345);
    check(0x0001'0001, 65537); check(0b1'00000001, 257);
    value = 2 +
            3;
    check(value, 5);
    return 0;
}
