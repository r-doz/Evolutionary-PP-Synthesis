parameters {
  real step;
}
model {
  step ~ normal(0,1);  
}
generated quantities {
  int x;
  x = 0;
  for (n in 1:10) {
	  if (step < 0.6745)
		x = x-1;
  	else
		x = x+1;
  }
}

