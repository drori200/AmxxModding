/* Predicted output: 0,1,0,65,66,0,2,84,116,0| (32-bit cell layout) */
bool:put_unpacked(buffer[], index, value, size=sizeof buffer)
{
    if (index<0 || index>=size-1)
        return false;
    buffer[index]=value;
    buffer[index+1]=0;
    return true;
}
main()
{
    var unpacked[4]=''A'';
    var packed{5}="test";
    var bool:a=put_unpacked(unpacked,-1,'X');
    var bool:b=put_unpacked(unpacked,1,'B');
    var bool:c=put_unpacked(unpacked,3,'Y');
    packed{0}='T';
    printf("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d|",a,b,c,unpacked[0],unpacked[1],unpacked[2],sizeof packed,packed{0},packed{3},packed{4});
}
