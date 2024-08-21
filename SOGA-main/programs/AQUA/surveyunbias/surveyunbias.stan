data {
  int<lower=0> N;
  vector<lower=1,upper=2>[N] personGender;
  vector<lower=0,upper=1>[N] dataAnswer;
}
parameters {
  vector<lower=0,upper=1>[2] bias;
}
model {

  bias[1] ~ beta(1,1);
  bias[2] ~ beta(1,1);
  
  dataAnswer[1] ~ bernoulli(bias[1]);
  dataAnswer[2] ~ bernoulli(bias[2]);
  dataAnswer[3] ~ bernoulli(bias[1]);
  dataAnswer[4] ~ bernoulli(bias[1]);
  dataAnswer[5] ~ bernoulli(bias[2]);

}
