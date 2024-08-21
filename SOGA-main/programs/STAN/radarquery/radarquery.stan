parameters {
	real<lower=0,upper=1> bi1;
      array[5] real<lower=0,upper=1> unif;
	real<lower=0,upper=10> x1;
	real x2;
	real<lower=-5, upper=0> a1;
      real<lower=0, upper=5> a2;
	real<lower=-1, upper=0> b1;
      real<lower=0, upper=1> b2;
	real<lower=-5, upper=0> c1;
      real<lower=0, upper=5> c2;
	real<lower=-5, upper=0> d1;
      real<lower=0, upper=5> d2;
	real<lower=-5, upper=0> e1;
      real<lower=0, upper=5> e2;
	real<lower=-1, upper=0> f1;
      real<lower=0, upper=1> f2;
	real<lower=-5, upper=0> g1;
      real<lower=0, upper=5> g2;
	real<lower=-5, upper=0> h1;
      real<lower=0, upper=5> h2;
}
transformed parameters {
      real a;
      a = a1 + a2;
      
      real b;
      b = b1 + b2;
	
      real c;
      c = c1 + c2;
	
      real d;
      d = d1 + d2;
	
      real e;
      e = e1 + e2;
      
      real f;
      f = f1 + f2;

      real g;
      g = g1 + g2;

      real h;
      h = h1 + h2;
}
model {
	bi1 ~ uniform(0,1);
      unif ~ uniform(0,1);

	real bi2;
	if (bi1 < 0.2) {
		bi2 = 1;
	} else {
		if (unif[1] < 0.2) {
			bi2 = 1;
		} else {
			bi2 = 0;
		}
	}
	x1 ~ uniform(0,10);
	x2 ~ normal(x1, 1.4142);

	array[2] real o;
	if (bi1 < 0.2) {
		if (unif[2] < 0.83) {
			target += a < 0? 1:0;
			o[1] = x1 + a;
		} else {
			target += b > 0? 1:0;
			o[1] = x1 + b;
		}
	} else {
		if (unif[3] < 0.5) {
			target += c < 0? 1:0;
			o[1] = x1 + c;
		} else {
			target += d > 0? 1:0;
			o[1] = x1 + d;
		}
	}

	if (bi2) {
		if (unif[4] < 0.83) {
			target += e < 0? 1:0;
			o[2] = x2 + e;
		} else {
			target += f > 0? 1:0;
			o[2] = x2 + f;
		}
	} else {
		if (unif[4] < 0.5) {
			target += g < 0? 1:0;
			o[2] = x2 + g;
		} else {
			target += h > 0? 1:0;
			o[2] = x2 + h;
		}
	}

	target += o[1] == 5 ? 1 : 0;
	target += bi1 == 1? 1 : 0;
}
