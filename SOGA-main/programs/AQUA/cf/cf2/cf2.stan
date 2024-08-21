data {
    int N;
    vector[N] y;

}
parameters {
    vector[5] mu;
}
model {
    mu ~ normal(0.0,5.0);
    y ~ normal(mu[1]*mu[2] + mu[3]*mu[4] + mu[5], 1.0);

}
