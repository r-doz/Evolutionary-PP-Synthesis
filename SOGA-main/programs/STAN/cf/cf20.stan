data {
    int N;
    vector[N] y;

}
parameters {
    vector[41] mu;
}
transformed parameters {
	real mean;
	mean = mu[1]*mu[2] + mu[3]*mu[4] + mu[5]*mu[6] + mu[7]*mu[8] + mu[9]*mu[10] + mu[11]*mu[12] + mu[11]*mu[12] + mu[13]*mu[14]  + mu[15]*mu[16]  + mu[17]*mu[18]  + mu[19]*mu[20] + mu[21]*mu[22] + mu[23]*mu[24] + mu[25]*mu[26] + mu[27]*mu[28] + mu[29]*mu[30] + mu[31]*mu[32] + mu[33]*mu[34] + mu[35]*mu[36] + mu[37]*mu[38] + mu[39]*mu[40] + mu[41];
}
model {
    mu ~ normal(0.0,5.0);
    y ~ normal(mean, 1.0);

}
