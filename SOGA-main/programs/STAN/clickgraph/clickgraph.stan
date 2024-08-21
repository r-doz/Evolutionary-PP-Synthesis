data {
  int N;
  array[N] int<lower=0,upper=1> click0;
  array[N] int<lower=0,upper=1> click1;
}
parameters {
  real<lower=0,upper=1> simAll;
  array[N] real<lower=0,upper=1> unif;
  real<lower=0,upper=1> beta1;
  real<lower=0,upper=1> beta2;
}

model {
  simAll ~ uniform(0,1);
  unif ~ uniform(0,1);	
  for (i in 1:N) {
      beta1 ~ uniform(0,1);
	if (unif[i] < simAll) {
		click0[i] ~ bernoulli(beta1);
  		click1[i] ~ bernoulli(beta1);
  	} else {
		beta2 ~ uniform(0,1);
		click0[i] ~ bernoulli(beta1);
  		click1[i] ~ bernoulli(beta2);
	}
  }
}
