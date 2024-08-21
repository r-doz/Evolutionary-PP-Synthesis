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
  real<lower = 0> y5;
}
model {
  alpha ~ normal(1,1);
  beta ~ normal(1,1);
  y2 ~ normal(alpha +  beta * x[2] +  lambda * y[1], 0.5);
  y3 ~ normal(alpha +  beta * x[3] +  lambda * y2, 0.5);
  y4 ~ normal(alpha +  beta * x[4] +  lambda * y3, 0.5);
  y5 ~ normal(alpha +  beta * x[5] +  lambda * y4, 0.5);
}

