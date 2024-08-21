data {
    int N;
    vector[N] y;

}
parameters {
    vector[3] mu;
}
model {
    mu ~ normal(0.0,5.0);
    y ~ normal(mu[1]*mu[2] + mu[3], 1.0);

}
