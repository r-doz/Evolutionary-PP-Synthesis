data {
}
parameters {
  real skillA;
  real skillB;
  real skillC;
  real perfA;
  real<upper=perfA> perfB;
  real<upper=perfA> perfC;
}
model {
  

  skillA ~ normal(100,10);
  skillB ~ normal(100,10);
  skillC ~ normal(100,10);

  perfA ~ normal(skillA, 15);
  perfB ~ normal(skillB, 15);
  perfC ~ normal(skillC, 15);
}
