data {
  int<lower=0> N;
  vector<lower=0,upper=1>[N] y; 
}
parameters {
  real<lower=0,upper=1> theta;
}
model {
  theta ~ uniform(0,1); 
  y ~ bernoulli(theta);
}
