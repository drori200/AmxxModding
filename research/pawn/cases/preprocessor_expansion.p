#include <lab>
#define OUTER(%0) (1 + INNER(%0))
#define INNER(%0) (2 * (%0))
#define MESSAGE(%0) "X" ... #%0
#tryinclude <research_intentionally_missing_optional_header>
#include <lab>
#if defined _inc_lab
    const included = 1;
#else
    #error implicit include guard constant missing
#endif
main()
{
    check(OUTER(8), 17);
    var message{} = MESSAGE(hi);
    check(message{0}, 'X'); check(message{1}, 'h');
    check(message{2}, 'i'); check(message{3}, 0);
    check(included, 1);
    return 0;
}
