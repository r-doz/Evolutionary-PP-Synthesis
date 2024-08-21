import pymc3 as pm
import arviz as az
import numpy as np
from time import time
import argparse

def getCliOptions():
    parser = argparse.ArgumentParser(description="Timeseries CLI")

    parser.add_argument("-o","--outputfile", help="Output file path",required=True)
    parser.add_argument("-n","--timesteps", type=int, default=2,required=False)

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args=getCliOptions()

    data_x = [0.0530897649405518, -0.427176340746955, 0.575506045064776, -1.05503057032362, -0.00138425373659317, 0.362367184144129, -0.906400668762085, 1.39464604836768, -1.40047244298115, -0.872458836353285, -0.425555167755021, -0.192907289991263, 0.611345320709905, 0.223493915844394, -0.335855643300744, -0.786177511979181, 1.0466888412128, -1.35578280849525, -0.4802662607177, -0.482825573577857, -0.44808934155094, 1.41677018342172, -1.12722529948411, -1.52518755310289, -0.232336215009525, -0.452482201859223, -0.235580964484178, -0.789514125170731, 1.61944620303219, 0.735756130006795, -1.0253656503392, 0.936124304383727, 1.10587169595422, 0.833182124741184, 0.113696178051401, -1.15636049024915, 1.85507312756962, 1.30957252757083, 0.822235075588577, -1.43800316565635]
    data_y = [-1.09070023335653, -2.49513228748069, -2.07918898737732, -3.34621083464711, -3.21905761756761, -3.84835139936697, -4.14591579938845, -2.17085702918779, -2.72986009710348, -2.35417403593087, -3.05798313015489, -2.85360404455837, -2.9261492993768, -2.67713444957349, -2.97731974867721, -4.7510500052692, -3.2939903406896, -4.11626048191435, -4.08086402479665, -3.34743297842617, -3.59294970060833, -1.70489370379594, -3.522911840642, -4.13944648650588, -4.04992280586435, -3.71707285571859, -2.6830205191276, -3.21920265745786, -1.78221835462429, -1.71385611701893, -3.15284681754168, -3.26094915407183, -2.92240028325557, -2.40186352631743, -3.1697331801915, -4.00540748111558, -2.32625323220302, -1.74827635320394, -1.05716214917384, -3.44536781268663]

    N = 3
    num_samples = 1000

    basic_model = pm.Model()

    with basic_model:
        alpha = pm.Normal('alpha', 1, 1)
        beta = pm.Normal('beta', 1, 1)
        lambda_ = pm.Uniform('lambda', 0, 1)
        y = [None] * N  # Placeholder for y1 to y6
        y[0] =  pm.Normal('y1', lambda_*data_y[0] + alpha + data_x[1]*beta, 0.5)
        for i in range(1,N):
            y[i] = pm.Normal('y{}'.format(i+1), lambda_*y[i-1] + alpha + data_x[i+1]*beta, 0.5)
        y_obs = pm.Bernoulli('y_obs', 0.99, observed=(y[N-1] > 0))
        
    start = time()
    idata=None
    samples=[]

    with basic_model:
        # Check convergence based on thresholds
        err_max=1.0
        err=10000

        while (err > err_max):
            # Additional sampling iterations
            idata = pm.sample(num_samples, chains=1)

            # Update diagnostics
            samples += idata['y{}'.format(N)].tolist()
            mean = np.mean(samples)
            std = np.std(samples)
            ci = 1.96*std/np.sqrt(len(samples))
            err = abs(ci*2)*100/mean
            print('Error with {} samples: {}'.format(len(samples), err))
            print('Estimated value: {}'.format(mean))
            

    end = time()
    outfile=open(args.outputfile,"w+")
    outfile.write("value,time,err\n")
    outfile.write(f"{np.round(mean,5)},{np.round(end-start,5)},{np.round(err,5)}\n")
    outfile.close()
