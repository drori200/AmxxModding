/* Predicted output: -3,2,-3,-2,|2,-3,-3| */
divmod(const input[], output[], count=sizeof input)
{
    for (var i=0; i<count; ++i)
    {
        var divisor = i % 2 ? -3 : 3;
        var original = input[i];
        output[i] = original / divisor;
        printf("%d,%d,", output[i], original % divisor);
    }
    return count;
}
main()
{
    var source[2]=[-7,7];
    var count=divmod(source, source);
    printf("|%d,%d,%d|",count,source[0],source[1]);
}
