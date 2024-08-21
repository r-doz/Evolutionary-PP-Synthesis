data toss = [1, 1, 0, 1, 0];

bias = beta([2, 5],$cmp); 

for i in range(5) {
    if uniform([0,1],$cmp) - bias < 0 {
        y = 1;
    } else {
        y = 0;
    } end if;

    observe(y == toss[i]);
    
} end for;



