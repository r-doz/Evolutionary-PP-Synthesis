// geometric lag time-series (Koyck 1951)
//
// http://en.wikipedia.org/wiki/Distributed_lag

data {
  int<lower=0> T;   // number of time points
  array[T] real y;        // output at time t
  array[T] real x;        // predictor for time t
}
parameters {
  real alpha;                       // intercept
  real beta;                        // slope
  real <lower=0, upper=1> lambda;   // lag
  real y2;
  real y3;
  real y4;
  real y5;
  real y6;
  real y7;
  real y8;
  real y9;
  real<lower=0> y10;
}
model {
  alpha ~ normal(1,1);
  beta ~ normal(1,1);
  y2 ~ normal(alpha +  beta * x[2] +  lambda * y[1], 0.5);
  y3 ~ normal(alpha +  beta * x[3] +  lambda * y2, 0.5);
  y4 ~ normal(alpha +  beta * x[4] +  lambda * y3, 0.5);
  y5 ~ normal(alpha +  beta * x[5] +  lambda * y4, 0.5);
  y6 ~ normal(alpha +  beta * x[6] +  lambda * y5, 0.5);
  y7 ~ normal(alpha +  beta * x[7] +  lambda * y6, 0.5);
  y8 ~ normal(alpha +  beta * x[8] +  lambda * y7, 0.5);
  y9 ~ normal(alpha +  beta * x[9] +  lambda * y8, 0.5);
  y10 ~ normal(alpha +  beta * x[10] +  lambda * y9, 0.5);
}