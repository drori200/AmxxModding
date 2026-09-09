#include <lab>
#define SCALE(%0) ((%0) * 3)
#define FEATURE_ENABLED
#if !defined FEATURE_ENABLED
    #error feature must be defined
#endif
#if cellbits != 16 && cellbits != 32 && cellbits != 64
    #error unexpected cell width
#endif
main()
{
    const value = 0x10 + 0b11;
    check(value, 19);
    check(SCALE(1 + 2), 9);
    check('a', 97);
    return 0;
}
