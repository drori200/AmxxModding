// Probe: the Language Guide p.53 says public globals are host-visible.
// Compiler7483 warns203 and omits storage if this variable is unreferenced.
public exposed = 7;
main() { return 0; }
