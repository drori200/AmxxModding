#include <lab>
main()
{
    var record[.points, .lives, .name{12}];
    record.points = 42;
    record[.lives] = 3;
    // Whole string-to-field assignment has a separate retained compiler/guide
    // disagreement. This positive fixture verifies explicit character access.
    record.name{0} = 'A'; record.name{1} = 'd';
    record.name{2} = 'a'; record.name{3} = 0;
    check(record[.points], 42);
    check(record.lives, 3);
    check(record.name{0}, 'A');
    check(record.name{3}, 0);
    check(sizeof record.name, 3);
    return 0;
}
