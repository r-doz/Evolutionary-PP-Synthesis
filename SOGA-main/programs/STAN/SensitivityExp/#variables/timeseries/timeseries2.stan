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
  real<lower=0> y3;
}
model {
  alpha ~ normal(1,1);
  beta ~ normal(1,1);
  y2 ~ normal(alpha +  beta * x[2] +  lambda * y[1], 0.5);
  y3 ~ normal(alpha +  beta * x[3] +  lambda * y2, 0.5);
}

