data {
    int N;
    vector[N] y;

}
parameters {
    vector[5] mu;
}
transformed parameters {
	real mean;
	mean = mu[1]*mu[2] + mu[3]*mu[4] + mu[5];
}
model {
    mu ~ normal(0.0,5.0);
    y ~ normal(mean, 1.0);

}
