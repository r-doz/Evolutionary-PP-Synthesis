data {
    int N;
    array[N] real y;

}
parameters {
    array[2] real<lower=-10, upper=10> mu;
}
model {
    mu ~ uniform(-10.0,10.0);
    y ~ normal((mu[1] + mu[2]), 1.0);

}
