parameters {
  real step;
}
model {
  step ~ uniform(0,1);  
}
generated quantities {
  int x;
  x = 0;
  for (n in 1:10) {
	  if (step < 0.75)
		x = x-1;
  	else
		x = x+1;
  }
}

