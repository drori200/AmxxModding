/* Predicted output: 37,37| */
Scaled:operator=(value)
    return Scaled:(value*10);
Scaled:operator+(Scaled:left,Scaled:right)
    return Scaled:(_:left+_:right);
Scaled:add(Scaled:first,Scaled:second)
    return first+second;
mutate(&Scaled:value)
    value=value+Scaled:5;
main()
{
    var Scaled:answer=add(3,Scaled:2);
    mutate(answer);
    var Scaled:mirror=answer;
    printf("%d,%d|",_:answer,_:mirror);
}
