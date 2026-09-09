#include <lab>
public exposed = 7;
forward @combine(left, right);
forward @mutate(values[], count);
forward @greet(text[]);
forward @packed_first(text{});
forward @give_error();

main() { check(exposed, 7); return 0; }
@combine(left, right) { return left * 10 + right; }
@mutate(values[], count)
{
    for (var index = 0; index < count; index++) values[index] += 10;
    return count;
}
@greet(text[]) { text[0] = 'Z'; return text[1]; }
@packed_first(text{}) { return text{0}; }
@give_error() { native_error(); return 0; }
