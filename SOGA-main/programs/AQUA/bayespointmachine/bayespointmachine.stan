data {
   int<lower=0> N;
   vector[N] feat1;
   vector[N] feat2;
   vector[N] feat3;
   vector[N] obs;
}
parameters {
  vector[3] w;
  vector[6] norm;
}
model {

w[1] ~ normal(0,1);
w[2] ~ normal(0,1);
w[3] ~ normal(0,1);
  
norm[1] ~ normal(feat1[1]*w[1]+feat2[1]*w[2]+feat3[1]*w[3],0.1);
norm[2] ~ normal(feat1[2]*w[1]+feat2[2]*w[2]+feat3[2]*w[3],0.1);
norm[3] ~ normal(feat1[3]*w[1]+feat2[3]*w[2]+feat3[3]*w[3],0.1);
norm[4] ~ normal(feat1[4]*w[1]+feat2[4]*w[2]+feat3[4]*w[3],0.1);
norm[5] ~ normal(feat1[5]*w[1]+feat2[5]*w[2]+feat3[5]*w[3],0.1);
norm[6] ~ normal(feat1[6]*w[1]+feat2[6]*w[2]+feat3[6]*w[3],0.1);

 for (i in 1:6) {
	obs[i] ~ bernoulli(norm[i] > 0);
 }

}