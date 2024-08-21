data {
  int<lower=0> N;
  array[N] int<lower=0,upper=1> obs; 
}
parameters {
  real<lower=0,upper=1> bias;
}
model {
  bias ~ beta(2,5);  
  obs ~ bernoulli(bias);
}
