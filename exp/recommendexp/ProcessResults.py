
import logging 
import sys 
import numpy 
import matplotlib 
matplotlib.use("GTK3Agg")
import matplotlib.pyplot as plt 
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc('text', usetex=True)
from apgl.util.PathDefaults import PathDefaults 



logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

#For now just print some results for a particular dataset 
dataset = "MovieLensDataset"
#dataset = "NetflixDataset"
#dataset = "SyntheticDataset1"
outputDir = PathDefaults.getOutputDir() + "recommend/" + dataset + "/"

plotStyles = ['k-', 'k--', 'k-.', 'r--', 'r-', 'g-', 'b-', 'b--', 'b-.', 'g--', 'g--', 'g-.', 'r-', 'r--', 'r-.']
methods = ["propack", "arpack", "rsvd", "rsvdUpdate"]

#pq = [(10, 2), (50, 2), (100, 2)]
pq = [(50, 2), (50, 3)]
#fileNames = [outputDir + "ResultsSgdMf.npz"]
#labels = ["SgdMf"]
fileNames = []
labels = []


for method in methods:
    if method == "propack" or method=="arpack": 
        fileName = outputDir + "ResultsSoftImpute_alg=" + method + ".npz"
        labels.append(method.upper())
        fileNames.append(fileName)
    else: 
        for p, q in pq: 
            fileName = outputDir + "ResultsSoftImpute_alg=" + method + "_p=" + str(p)+ "_q=" + str(q) + ".npz"
            if method == "rsvd": 
                labels.append("RSVD p=" + str(p)+ " q=" + str(q))
            else: 
                labels.append("RSVD+ p=" + str(p)+ " q=" + str(q))
            fileNames.append(fileName)
       
i = 0       
       
for j, fileName in enumerate(fileNames): 
    try: 
        data = numpy.load(fileName)
        logging.debug("Loaded " + str(fileName))
        measures = data["arr_0"]
        metadata = data["arr_1"]
        
        try: 
            vectorMetadata = data["arr_2"]
            vectorMetadata = vectorMetadata[:, 0:9, :]
            meanVectorMetadata = vectorMetadata.mean(0)
            stdVectorMetadata = vectorMetadata.std(0)
            print(meanVectorMetadata)
        except: 
            pass 
        
        print("rho = " + str(metadata[0,1]) +  " rank = " + str(metadata[0, 0])) 
        print(measures[:, 0])
        
        plt.figure(0)
        plt.plot(numpy.arange(measures.shape[0]), measures[:, 0], plotStyles[i], label=labels[j])
        plt.xlabel("Matrix no.")        
        plt.ylabel("RMSE Test")
        plt.legend(loc="upper right") 
        plt.savefig(outputDir + dataset + "RMSETest.eps")
        
        plt.figure(1)
        plt.plot(numpy.arange(measures.shape[0]), measures[:, 1], plotStyles[i], label=labels[j])
        plt.xlabel("Matrix no.")        
        plt.ylabel("MAE Test")
        plt.legend(loc="lower left") 
        
        if measures.shape[1] == 3:
            plt.figure(2)
            plt.plot(numpy.arange(measures.shape[0]), measures[:, 2], plotStyles[i], label=labels[j])
            plt.legend(loc="upper left") 
            plt.xlabel("Matrix no.")
            plt.ylabel("RMSE Train")
            plt.savefig(outputDir + dataset + "RMSETrain.eps")
        
        plt.figure(3)
        plt.plot(numpy.arange(metadata.shape[0]), metadata[:, 0], plotStyles[i], label=labels[j])
        plt.legend() 
        plt.xlabel("Matrix no.")
        plt.ylabel("Rank")
        
        plt.figure(4)
        plt.plot(numpy.arange(metadata.shape[0]), numpy.log10(numpy.cumsum(metadata[:, 2])), plotStyles[i], label=labels[j])
        plt.legend(loc="lower right") 
        plt.xlabel("Matrix no.")
        plt.ylabel("log(time) (s)")
        print("time="+str(numpy.cumsum(metadata[:, 2])))
        plt.savefig(outputDir + dataset + "Times.eps")
        
        try: 
            if labels[j] == "PROPACK" and "meanVectorMetadata" in locals():
                plt.figure(5)
                plt.plot(numpy.arange(meanVectorMetadata.shape[0]), numpy.log10(meanVectorMetadata[:, 0]), plotStyles[0], label=r"$\gamma$")
                plt.plot(numpy.arange(meanVectorMetadata.shape[0]), numpy.log10(meanVectorMetadata[:, 1]), plotStyles[1], label=r"$\theta_P$")
                plt.plot(numpy.arange(meanVectorMetadata.shape[0]), numpy.log10(meanVectorMetadata[:, 2]), plotStyles[2], label=r"$\theta_Q$")
                plt.plot(numpy.arange(meanVectorMetadata.shape[0]), numpy.log10(meanVectorMetadata[:, 3]), plotStyles[3], label=r"$\phi_\sigma$")
                plt.legend(loc="upper right") 
                plt.xlabel("Iteration")
                plt.ylabel("log(change)")
                plt.savefig(outputDir + dataset + "Subspace.eps")
        except: 
            raise
            
        data = numpy.load(fileName.replace("Results", "ModelSelect"))
        logging.debug("Loaded " + str(fileName))
        means = data["arr_0"]
        stds = data["arr_1"]            
        
        plt.figure(6+i)
        ks = numpy.array(2**numpy.arange(3.5, 7.5, 0.5), numpy.int) 
        rhos = numpy.linspace(0.5, 0.0, 6) 
        plt.contourf(ks, rhos, means, antialiased=True)
        plt.xlabel("k")
        plt.ylabel(r"$\rho$")
        plt.colorbar()
        print(means)
        plt.savefig((outputDir + dataset + "MS_" + str(labels[j]) + ".eps").replace(" ", "_"))
        
        i += 1
        
    except IOError as e:
        logging.debug(e)
       

plt.show()
