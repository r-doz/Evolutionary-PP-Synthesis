data {
    int N;
    vector[N] y;

}
parameters {
    vector[11] mu;
}
transformed parameters {
	real mean;
	mean = mu[1]*mu[2] + mu[3]*mu[4] + mu[5]*mu[6] + mu[7]*mu[8] + mu[9]*mu[10] + mu[11];
}
model {
    mu ~ normal(0.0,5.0);
    y ~ normal(mean, 1.0);

}
