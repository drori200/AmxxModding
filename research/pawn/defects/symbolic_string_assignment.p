// August2025 Language Guide p.56 permits string assignment to a named field.
// This compiler rejects the following with047 despite sufficient capacity.
main()
{
    var record[.name{12}];
    record.name = "Ada";
    return record.name{0};
}
