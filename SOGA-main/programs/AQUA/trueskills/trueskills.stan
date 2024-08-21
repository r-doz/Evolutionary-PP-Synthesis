data {
  vector[2] y;
}
parameters {
  real skillA;
  real skillB;
  real skillC;
  real perfA;
  real perfB;
  real perfC;
}
model {

  skillA ~ normal(100,10);
  skillB ~ normal(100,10);
  skillC ~ normal(100,10);
  perfA ~ normal(skillA, 15);
  perfB ~ normal(skillB, 15);
  perfC ~ normal(skillC, 15);
  y[1] ~ bernoulli(perfA > perfB);
  y[2] ~ bernoulli(perfA > perfC); 
}
