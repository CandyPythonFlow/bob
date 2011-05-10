/// @file Gaussian.h
/// @author <a href="mailto:Roy.Wallace@idiap.ch">Roy Wallace</a> 
/// @brief This class implements a multivariate diagonal Gaussian distribution. 

#ifndef _GAUSSIAN_H
#define _GAUSSIAN_H

#include <blitz/array.h>
#include <cfloat>

namespace Torch {
namespace machine {

namespace Log
{
  #define MINUS_LOG_THRESHOLD -39.14
  
  const double Log2Pi = 1.83787706640934548355;
  const double LogZero = -DBL_MAX;
  const double LogOne = 0;
  
  double LogAdd(double log_a, double log_b);
  double LogSub(double log_a, double log_b);
}

/// @brief This class implements a multivariate diagonal Gaussian distribution. 
class Gaussian {
  public:

    /// Default constructor
    Gaussian();

    /// Constructor
    /// @param[in] n_inputs The feature dimensionality
    Gaussian(int n_inputs);

    /// Destructor
    virtual ~Gaussian();

    /// Copy constructor
    Gaussian(const Gaussian& other);

    /// Assigment
    Gaussian& operator= (const Gaussian &other);
    
    /// Set the feature dimensionality
    /// Overrides Machine::setNInputs
    void setNInputs(int n_inputs);

    /// Set the input dimensionality, reset the mean to zero
    /// and the variance to one.
    /// @param n_inputs The feature dimensionality
    bool resize(int n_inputs);

    /// Set the mean
    bool setMean(const blitz::Array<double,1> &mean);

    /// Set the variance
    bool setVariance(const blitz::Array<double,1> &variance);

    /// Set the variance flooring thresholds
    bool setVarianceThresholds(const blitz::Array<double,1> &variance_thresholds);

    /// Set the variance flooring thresholds
    bool setVarianceThresholds(double factor);

    /// Output the log likelihood of the sample, x 
    /// @param x The data sample (feature vector)
    double logLikelihood(const blitz::Array<float,1> &x) const;

    /// Output the logLikelihood of the sample, x 
    /// (overrides Machine::forward)
    double forward(const blitz::Array<float,1> &input) const;

    /// Get the variance flooring thresholds
    bool getVarianceThresholds(blitz::Array<double,1> &variance_thresholds) const;

    /// Get the mean
    bool getMean(blitz::Array<double,1> &mean) const;

    /// Get the variance (the diagonal of the covariance matrix)
    bool getVariance(blitz::Array<double,1> &variance) const;

    /// Print the mean and variance of the Gaussian
    bool print() const;

  protected:

    /// Copy another Gaussian
    void copy(const Gaussian& other);
    
    /// Compute and store the value of g_norm, 
    /// to later speed up evaluation of logLikelihood()
    /// Note: g_norm is defined as follows:
    /// log(Gaussian pdf) = log(1/((2pi)^(k/2)(det)^(1/2)) * exp(...))
    ///                   = -1/2 * g_norm * (...)
    bool preComputeConstants();

    /// The mean
    blitz::Array<double,1> m_mean;

    /// The diagonal of the covariance matrix
    blitz::Array<double,1> m_variance;

    /// The variance flooring thresholds, i.e. the minimum allowed
    /// value of variance in each dimension.
    /// The variance will be set to this value if an attempt is made
    /// to set it to a smaller value.
    blitz::Array<double,1> m_variance_thresholds;

    /// A constant that depends only on the feature dimensionality
    /// (m_n_inputs) and the variance
    /// @see bool preComputeConstants()
    double g_norm;

    /// The number of inputs
    int m_n_inputs;
};

}
}
#endif
