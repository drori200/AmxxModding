#include <lab>
// Deliberate invalid access. Only allowed in checked VM profiles by manifest.
main() { var values[] = [1, 2]; return values[identity(-1)]; }
