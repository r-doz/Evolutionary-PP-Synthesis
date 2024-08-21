data {
  int<lower=0> N;
  array[N] int<lower=1,upper=2> personGender;
  array[N] int<lower=0,upper=1> dataAnswer;
}
parameters {
  array[2] real<lower=0,upper=1> bias;
}
model {

  bias[1] ~ beta(1,1);
  bias[2] ~ beta(1,1);
  
  for (n in 1:N) {
         dataAnswer[n] ~ bernoulli(bias[personGender[n]]);
  }

}
