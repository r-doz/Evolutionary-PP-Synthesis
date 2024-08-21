data {
   int<lower=0> N;
   array[N] int feat1;
   array[N] int feat2;
   array[N] int feat3;
   array[N] real obs;
}
parameters {
  array[3] real w;
  real<lower=0> norm1;
  real<upper=0> norm2;
  real<lower=0> norm3;
  real<lower=0> norm4;
  real<upper=0> norm5;
  real<upper=0> norm6;
}
model {

  for (i in 1:3) {
  	w[i] ~ normal(0,1);
  }
  
 norm1 ~ normal(feat1[1]*w[1] + feat2[1]*w[2] + feat3[1]*w[3],0.1);
 norm2 ~ normal(feat1[2]*w[1] + feat2[2]*w[2] + feat3[2]*w[3],0.1);
 norm3 ~ normal(feat1[3]*w[1] + feat2[3]*w[2] + feat3[3]*w[3],0.1);
 norm4 ~ normal(feat1[4]*w[1] + feat2[4]*w[2] + feat3[4]*w[3],0.1);
 norm5 ~ normal(feat1[5]*w[1] + feat2[5]*w[2] + feat3[5]*w[3],0.1);
 norm6 ~ normal(feat1[6]*w[1] + feat2[6]*w[2] + feat3[6]*w[3],0.1);

}