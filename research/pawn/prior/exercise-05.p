/* Predicted output: 1,0,5,5,3,24| */
#define DUP(%1) ((%1)+(%1))
var hits;
bump() { return ++hits; }
factorial(n)
{
    if (n<=1) return 1;
    return n*factorial(n-1);
}
main()
{
    var bool:inside=(0<=bump()<3);
    var x;
    var bool:skipped=(x && bump());
    var y=(x=4,x+1);
    var doubled=DUP(bump());
    printf("%d,%d,%d,%d,%d,%d|",inside,skipped,y,doubled,hits,factorial(4));
}
