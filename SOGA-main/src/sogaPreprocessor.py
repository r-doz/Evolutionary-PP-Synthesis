# A parser that produce a .soga file from a high-level to low-level syntax
import re
import numpy as np
from sklearn.mixture import GaussianMixture
from joblib import parallel_backend
import tempfile
from functools import partial

nsamples=int(10**7)
computedDist={}

def extractMatch(input_prog,regex):
	matches = re.finditer(regex, input_prog, re.MULTILINE)
	inMatches=[]
	oText=[]
	for matchNum, match in enumerate(matches, start=1):
		oText+=[input_prog[match.start():match.end()]]
		for groupNum in range(0, len(match.groups())):
			groupNum = groupNum + 1
			inMatches+=[match.group(groupNum)]
	return inMatches,oText

def compileUniform(input_prog):
	global computedDist
	#uniform([low,high], ncmp)
	matches,oText=extractMatch(input_prog,regex = r"uniform\((.*?)\)")
	for idx,m in enumerate(matches):
		m_k=m.replace(" ","")
		if(f"uniform({m_k})" not in computedDist):
			res=re.split(r"(?<=\])\s*,",m)
			
			low=float(res[0].split(",")[0].replace("[","").strip())
			high=float(res[0].split(",")[1].replace("]","").strip())
			ncmp=int(res[1].strip())

			X=np.random.uniform(low=low, high=high,size=nsamples).reshape(-1, 1)
			weights,means,covariances=fitGmm(X,ncmp)

			input_prog=input_prog.replace(oText[idx],
					 "gm([%s],[%s],[%s])"%(",".join(map(lambda x:"%.10f"%(x),weights)),",".join(map(lambda x:"%.10f"%(x),means)),
					 ",".join(map(lambda x:"%.10f"%(x),(np.sqrt(covariances))))))

			computedDist[f"uniform({m_k})"]=[weights,means,covariances]
		else:
			#print("all done")
			w=computedDist[f"uniform({m_k})"][0]
			mu=computedDist[f"uniform({m_k})"][1]
			cov=computedDist[f"uniform({m_k})"][2]

			input_prog=input_prog.replace(oText[idx],
					 "gm([%s],[%s],[%s])"%(",".join(map(lambda x:"%.10f"%(x),w)),",".join(map(lambda x:"%.10f"%(x),mu)),
					 ",".join(map(lambda x:"%.10f"%(x),(np.sqrt(cov))))))

	return input_prog

def compileBeta(input_prog):
	global computedDist
	#beta([a,b], ncmp)
	matches,oText=extractMatch(input_prog,regex = r"beta\((.*?)\)")
	for idx,m in enumerate(matches):
		m_k=m.replace(" ","")
		if(f"beta({m_k})" not in computedDist):
			res=re.split(r"(?<=\])\s*,",m)
			a=float(res[0].split(",")[0].replace("[","").strip())
			b=float(res[0].split(",")[1].replace("]","").strip())
			ncmp=int(res[1].strip())

			X=np.random.beta(a, b,size=nsamples).reshape(-1, 1)
			weights,means,covariances=fitGmm(X,ncmp)

			input_prog=input_prog.replace(oText[idx],
					 "gm([%s],[%s],[%s])"%(",".join(map(lambda x:"%.10f"%(x),weights)),",".join(map(lambda x:"%.10f"%(x),means)),
					 ",".join(map(lambda x:"%.10f"%(x),(np.sqrt(covariances))))))

			computedDist[f"beta({m_k})"]=[weights,means,covariances]
		else:
			w=computedDist[f"beta({m_k})"][0]
			mu=computedDist[f"beta({m_k})"][1]
			cov=computedDist[f"beta({m_k})"][2]

			input_prog=input_prog.replace(oText[idx],
					 "gm([%s],[%s],[%s])"%(",".join(map(lambda x:"%.10f"%(x),w)),",".join(map(lambda x:"%.10f"%(x),mu)),
					 ",".join(map(lambda x:"%.10f"%(x),(np.sqrt(cov))))))

	return input_prog

def compileLaplace(input_prog):
    global computedDist
    #laplace(loc, scale, ncmp)
    matches,oText=extractMatch(input_prog,regex = r"laplace\((.*?)\)")
    for idx,m in enumerate(matches):
        m_k=m.replace(" ","")
        if(f"laplace({m_k})" not in computedDist):
            loc, scale, ncmp = m.split(",")
            X=np.random.laplace(float(loc), float(scale), nsamples).reshape(-1, 1)
            weights,means,covariances=fitGmm(X,int(ncmp))
            input_prog=input_prog.replace(oText[idx],
             "gm([%s],[%s],[%s])"%(",".join(map(lambda x:"%.10f"%(x),weights)),",".join(map(lambda x:"%.10f"%(x),means)),
             ",".join(map(lambda x:"%.10f"%(x),(np.sqrt(covariances))))))
            computedDist[f"laplace({m_k})"]=[weights,means,covariances]
        else:
            #print("all done")
            w=computedDist[f"laplace({m_k})"][0]
            mu=computedDist[f"laplace({m_k})"][1]
            cov=computedDist[f"laplace({m_k})"][2]
            input_prog=input_prog.replace(oText[idx],
                 "gm([%s],[%s],[%s])"%(",".join(map(lambda x:"%.10f"%(x),w)),",".join(map(lambda x:"%.10f"%(x),mu)),
                 ",".join(map(lambda x:"%.10f"%(x),(np.sqrt(cov))))))
    return input_prog

def compileExpRnd(input_prog):
	global computedDist
	#exprnd(scale,ncmp)
	matches,oText=extractMatch(input_prog,regex = r"exprnd\((.*?)\)")
	for idx,m in enumerate(matches):
		m_k=m.replace(" ","")
		if(f"exprnd({m_k})" not in computedDist):
			X=np.random.exponential(float(m.split(",")[0].strip()),nsamples).reshape(-1, 1)
			weights,means,covariances=fitGmm(X,int(m.split(",")[1].strip()))

			input_prog=input_prog.replace(oText[idx],
					 "gm([%s],[%s],[%s])"%(",".join(map(lambda x:"%.10f"%(x),weights)),",".join(map(lambda x:"%.10f"%(x),means)),
					 ",".join(map(lambda x:"%.10f"%(x),(np.sqrt(covariances))))))

			computedDist[f"exprnd({m_k})"]=[weights,means,covariances]
		else:
			w=computedDist[f"exprnd({m_k})"][0]
			mu=computedDist[f"exprnd({m_k})"][1]
			cov=computedDist[f"exprnd({m_k})"][2]

			input_prog=input_prog.replace(oText[idx],
					 "gm([%s],[%s],[%s])"%(",".join(map(lambda x:"%.10f"%(x),w)),",".join(map(lambda x:"%.10f"%(x),mu)),
					 ",".join(map(lambda x:"%.10f"%(x),(np.sqrt(cov))))))

	return input_prog

def compileBernoulli(input_prog):
	#bern(p)
	matches,oText=extractMatch(input_prog,regex = r"bern\((.*?)\)")
	for idx,m in enumerate(matches):
		p=float(m.split(",")[0].strip())
		input_prog=input_prog.replace(oText[idx],
			"gm([%f,%f],[0.0,1.0],[0.0,0.0])"%(1-p,p,))
	
	return input_prog

def compileGauss(input_prog):
	#gauss(mean,std)
	matches,oText=extractMatch(input_prog,regex = r"gauss\((.*?)\)")
	for idx,m in enumerate(matches):
		mean=float(m.split(",")[0].strip())
		std=float(m.split(",")[1].strip())

		input_prog=input_prog.replace(oText[idx],
			"gm([1.0],[%f],[%f])"%(mean,std))
	
	return input_prog


def fitGmm(X=None,ncomp=2):
	gmm = GaussianMixture(n_components=ncomp,max_iter=1000,n_init=1,
							  covariance_type='full')#,init_params="k-means++")
	gmm.fit(X)

	# Access parameters
	means = gmm.means_.flatten()
	weights = gmm.weights_.flatten()
	covariances = gmm.covariances_.flatten()

	return weights,means,covariances


def compile2SOGA(input_prog):
    progr=open(input_prog,"r").read()
    progr=compileExpRnd(input_prog=progr)
    progr=compileUniform(input_prog=progr)
    progr=compileBeta(input_prog=progr)
    progr=compileLaplace(input_prog=progr)

    progr=compileGauss(input_prog=progr)
    progr=compileBernoulli(input_prog=progr)

    temp_file=tempfile.NamedTemporaryFile(mode='w',delete=False)
    temp_file.write(progr)
    temp_file.close()

    return temp_file.name

if __name__ == '__main__':

	import matplotlib.pyplot as plt
	from scipy.stats import uniform
	from scipy.stats import norm
	import json

	# Plot function
	def plot_mixture(gmm, X=None, show_legend=True, ax=None):
		if ax is None:
			ax = plt.gca()

		# Compute PDF of whole mixture
		x = np.linspace(-6, 6, 1000)
		logprob = gmm.score_samples(x.reshape(-1, 1))
		pdf = np.exp(logprob)

		# Compute PDF for each component
		responsibilities = gmm.predict_proba(x.reshape(-1, 1))
		pdf_individual = responsibilities * pdf[:, np.newaxis]
		# Plot data histogram
		#ax.hist(X, 30, density=True, histtype='stepfilled', alpha=0.4, label='Data')

		# Plot PDF of whole model
		ax.plot(x, pdf, '-k', label='Mixture PDF')

		# Plot PDF of each component
		ax.plot(x, pdf_individual, '--', label='Component PDF')
		ax.set_xlabel('$x$')
		ax.set_ylabel('$p(x)$')
		if show_legend:
			ax.legend()

	def getText(a,b,N):
		""" converts string "uniform([a,b], K)" in "gm(pi, mu, sigma)" where gm is a Gaussian Mix with K component approximating the uniform"""
		# a = float(self.list_().NUM()[0].getText())
		# b = float(self.list_().NUM()[1].getText())
		# N = int(self.NUM().getText())
		pi = [round(1.0/N,4)]*N
		mu = [round(a+i*(b-a)/N+((b-a)/(2*N)),4) for i in range(N)]
		sigma = list([round((b-a)/(np.sqrt(12)*N),4)]*N)
		return 'gm('+str(pi)+','+str(mu)+','+str(sigma)+')'

	def createGMM(mean,std):
		return [ norm(loc=mean[i], scale=std[i]) for i in range(len(mean))]

	def getGMM_PDF(gmm,weights,X):
		pdf_val=[]
		for x in X:
			pdf_val+=[0]
			for i in range(len(gmm)):
				pdf_val[-1]+=weights[i] * gmm[i].pdf(x)
		return pdf_val

	gmEM=compileUniform(input_prog="uniform([0,1], 5)")
	gmFr=getText(a=0,b=1,N=5)

	res=re.split(r"(?<=\])\s*,",gmEM.replace("gm","").replace("(","").replace(")",""))
	w1=json.loads(res[0])
	mu1=json.loads(res[1])
	std1=json.loads(res[2])

	res=re.split(r"(?<=\])\s*,",gmFr.replace("gm","").replace("(","").replace(")",""))
	w2=json.loads(res[0])
	mu2=json.loads(res[1])
	std2=json.loads(res[2])

	gmm1=createGMM(mu1,std1)
	gmm2=createGMM(mu2,std2)

	uni=uniform()

	x_axis = np.linspace(-2,3, 1000)
	pdf1=getGMM_PDF(gmm1,w1,x_axis)
	pdf2=getGMM_PDF(gmm2,w2,x_axis)

	plt.plot(x_axis, pdf1,'-', lw=1.5, alpha=1.0, label='pdf_fit')
	plt.plot(x_axis, pdf2,'-', lw=1.5, alpha=0.6, label='pdf_fra')
	plt.plot(x_axis, uni.pdf(x_axis),'-', lw=1.5, alpha=0.6, label='pdf_uni')
	plt.legend()
	plt.grid()
	plt.show()

	#plot_mixture(gmm1)





	