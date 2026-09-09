/* Predicted output: 12341,1,2| */
var trace;
entry() <flow:idle> { trace=trace*10+1; }
exit() <flow:idle> { trace=trace*10+2; }
entry() <flow:busy> { trace=trace*10+3; }
exit() <flow:busy> { trace=trace*10+4; }
tick()
{
    static calls;
    return ++calls;
}
work() <flow:idle>
{
    state flow:busy;
    return tick();
}
work() <flow:busy>
{
    state flow:idle;
    return tick();
}
work() <> { return -1; }
main()
{
    state flow:idle;
    var first=work();
    var second=work();
    printf("%d,%d,%d|",trace,first,second);
}
