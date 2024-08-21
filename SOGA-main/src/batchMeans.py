import numpy as np
from scipy import stats


def batch_means_conf_interval(data, batch_size, confidence_level=0.05):
  """
  This function implements the batch means algorithm and calculates the confidence interval for each feature.

  Args:
      data: A NumPy array of shape (num_samples, feature_dim).
      batch_size: The size of the batches.
      confidence_level: The confidence level for the confidence interval (default: 0.95).

  Returns:
      A tuple containing:
          - batch_means: A NumPy array of shape (num_batches, feature_dim) containing the means of each batch.
          - conf_intervals: A NumPy array of shape (num_batches, feature_dim, 2) containing the lower and upper bounds of the confidence interval for each feature in each batch.
  """

  num_samples, feature_dim = data.shape
  num_batches=None
  if((num_samples % batch_size)==0):
    num_batches = num_samples // batch_size
  else:
    num_batches = int(np.floor(num_samples/batch_size))
    data=data[0:num_batches*batch_size,:]


  # Reshape the data into batches
  data_reshaped = data.reshape(num_batches, batch_size, feature_dim)

  # Calculate the mean and standard deviation of each batch
  batch_means = np.mean(data_reshaped, axis=1)
  margin_of_error = np.std(batch_means,axis=0) * np.sqrt(1 - confidence_level) / np.sqrt(batch_means.shape[0])
  err=(margin_of_error/np.mean(batch_means,axis=0))*100

  return np.mean(batch_means,axis=0),batch_means.mean(axis=0) - margin_of_error,batch_means.mean(axis=0) + margin_of_error,err

if __name__ == '__main__':
  # Example usage
  data = np.random.rand(856, 5)  # Generate random data
  batch_size = 30
  confidence_level = 0.05

  batch_means_result,lw, up, err = batch_means_conf_interval(data, batch_size, confidence_level)
  print(err)

