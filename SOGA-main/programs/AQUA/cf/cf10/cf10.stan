data {
    int N;
    vector[N] y;

}
parameters {
    vector[21] mu;
}
transformed parameters {
	real mean;
	mean = mu[1]*mu[2] + mu[3]*mu[4] + mu[5]*mu[6] + mu[7]*mu[8] + mu[9]*mu[10] + mu[11]*mu[12] + mu[11]*mu[12] + mu[13]*mu[14]  + mu[15]*mu[16]  + mu[17]*mu[18]  + mu[19]*mu[20] + mu[21];
}
model {
    mu ~ normal(0.0,5.0);
    y ~ normal(mean, 1.0);

}
