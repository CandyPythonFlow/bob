#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed  9 Mar 08:49:39 2011 

"""Tests our Optical Flow utilities going through some example data.
"""

import os, sys
import unittest
import torch

def load_gray(relative_filename):
  # Please note our PNG loader will always load in RGB, but since that is a
  # grayscaled version of the image, I just select one of the planes. 
  filename = os.path.join("data", "flow", relative_filename)
  array = torch.io.Array(filename)
  return array.get()[0,:,:] 

def load_known_flow(relative_filename):
  filename = os.path.join("data", "flow", relative_filename)
  array = torch.io.Array(filename)
  data = array.get()
  return data[:,:,0].cast('float64'), data[:,:,1].cast('float64')

def make_image_tripplet():
  """Creates two images for you to calculate the flow
  
  10 10 10 10 10    10 10 10 10 10    10 10 10 10 10
  10  5  5  5  5    10 10 10 10 10    10 10 10 10 10
  10  5  5  5  5 => 10 10  5  5  5 => 10 10 10 10 10
  10 10 10 10 10    10 10  5  5  5    10 10 10  5  5
  10 10 10 10 10    10 10 10 10 10    10 10 10  5  5
  
  """
  im1 = torch.core.array.uint8_2(5,5)
  im1.fill(10)
  im1[1:3, 1:] = 5
  im2 = torch.core.array.uint8_2(5,5)
  im2.fill(10)
  im2[2:4, 2:] = 5
  im3 = torch.core.array.uint8_2(5,5)
  im3.fill(10)
  im3[3:, 3:] = 5
  return im1.cast('float64'), im2.cast('float64'), im3.cast('float64')

def HornAndSchunckFlowPython(alpha, im1, im2, im3, u0, v0):
  """Calculates the H&S flow in pure python"""
  grad = torch.ip.HornAndSchunckGradient(im1.shape())
  ex, ey, et = grad(im1, im2)
  ex *= 0.25
  ey *= 0.25
  et *= 0.25
  #u = torch.ip.laplacian_12(u0) / -12.
  #v = torch.ip.laplacian_12(v0) / -12.
  u = torch.ip.laplacian_014(u0) / -0.25
  v = torch.ip.laplacian_014(v0) / -0.25
  common_term = (ex*u + ey*v + et) / (ex**2 + ey**2 + alpha**2)
  return u - ex*common_term, v - ey*common_term

def compute_flow_opencv(alpha, iterations, ifile1, ifile2):
  import cv
  i1 = cv.LoadImageM(os.path.join("data", "flow", ifile1), iscolor=False)
  i2 = cv.LoadImageM(os.path.join("data", "flow", ifile2), iscolor=False)
  u = cv.CreateMat(i1.rows, i1.cols, cv.CV_32F)
  cv.SetZero(u)
  v = cv.CreateMat(i1.rows, i1.cols, cv.CV_32F)
  cv.SetZero(v)
  l = 1.0/(alpha**2)
  cv.CalcOpticalFlowHS(i1, i2, 0, u, v, l, (cv.CV_TERMCRIT_ITER, iterations, 0))
  # return blitz arrays
  return torch.core.array.array(u, 'float64'), torch.core.array.array(v, 'float64')

class FlowTest(unittest.TestCase):
  """Performs various combined optical flow tests."""

  def notest01_HornAndSchunckAgainstSyntheticPython(self):
    
    # Tests and examplifies usage of the vanilla HS algorithm while comparing
    # the C++ implementation to a pythonic implementation of the same algorithm

    # We create a new estimator specifying the alpha parameter (first value)
    # and the number of iterations to perform (second value).
    N = 100
    alpha = 15. 

    # The OpticalFlow estimator always receives a blitz::Array<uint8_t,2> as
    # the image input. The output has the same rank and extents but is in
    # doubles.
    i1, i2, i3 = make_image_tripplet()
    u_cxx = torch.core.array.float64_2(i1.shape()); u_cxx.fill(0)
    v_cxx = torch.core.array.float64_2(i1.shape()); v_cxx.fill(0)
    u_py = torch.core.array.float64_2(i1.shape()); u_py.fill(0)
    v_py = torch.core.array.float64_2(i1.shape()); v_py.fill(0)
    flow = torch.ip.VanillaHornAndSchunckFlow(i1.shape())
    for i in range(N):
      flow(alpha, 1, i1, i2, u_cxx, v_cxx)
      u_py, v_py = HornAndSchunckFlowPython(alpha, i1, i2, i3, u_py, v_py)
      #cxx_se2 = flow.evalEc2(u_cxx, v_cxx)
      #cxx_be = flow.evalEb(i1, i2, u_cxx, v_cxx)
      #py_se2 = flow.evalEc2(u_py, v_py)
      #py_be = flow.evalEb(i1, i2, u_py, v_py)
      #cxx_avg_err = (cxx_se2 * (alpha**2) + cxx_be**2).sum()
      #py_avg_err = (py_se2 * (alpha**2) + py_be**2).sum()
      #print "Error %2d: %.3e (%.3e) %.3e (%.3e) %.3e (%.3e)" % \
      #    (
      #     i, 
      #     cxx_se2.sum()**0.5,
      #     py_se2.sum()**0.5, 
      #     cxx_be.sum(), 
      #     py_be.sum(), 
      #     cxx_avg_err**0.5,
      #     py_avg_err**0.5
      #    )
    self.assertTrue( u_cxx.numeq(u_py) )
    self.assertTrue( v_cxx.numeq(v_py) )

  def notest02_VanillaHornAndSchunckDemo(self):
    
    N = 64
    alpha = 2 

    if1 = os.path.join("rubberwhale", "frame10_gray.png")
    if2 = os.path.join("rubberwhale", "frame11_gray.png")
    i1 = load_gray(if1)
    i2 = load_gray(if2)

    u = torch.core.array.float64_2(i1.shape()); u.fill(0)
    v = torch.core.array.float64_2(i1.shape()); v.fill(0)
    flow = torch.ip.VanillaHornAndSchunckFlow(i1.shape())
    for k in range(N): 
      flow(alpha, 1, i1, i2, u, v)
      array = (255.0*torch.ip.flowutils.flow2hsv(u,v)).cast('uint8')
      array.save("hs_rubberwhale-%d.png" % k)

  def notest03_VanillaHornAndSchunckAgainstOpenCV(self):
    
    # Tests and examplifies usage of the vanilla HS algorithm while comparing
    # the C++ implementation to a OpenCV implementation of the same algorithm.
    # Please note that the comparision is not fair as the OpenCV uses
    # different kernels for the evaluation of the image gradient.

    # This test is only here to help you debug problems.

    # We create a new estimator specifying the alpha parameter (first value)
    # and the number of iterations to perform (second value).
    N = 5 
    alpha = 15 

    # The OpticalFlow estimator always receives a blitz::Array<uint8_t,2> as
    # the image input. The output has the same rank and extents but is in
    # doubles.
    
    # This will load the test images: Rubber Whale sequence
    if1 = os.path.join("rubberwhale", "frame10_gray.png")
    if2 = os.path.join("rubberwhale", "frame11_gray.png")
    i1 = load_gray(if1)
    i2 = load_gray(if2)

    u_cxx = torch.core.array.float64_2(i1.shape()); u_cxx.fill(0)
    v_cxx = torch.core.array.float64_2(i1.shape()); v_cxx.fill(0)
    flow = torch.ip.VanillaHornAndSchunckFlow(i1.shape())
    flow(alpha, N, i1, i2, u_cxx, v_cxx)
    se2 = flow.evalEc2(u_cxx, v_cxx)
    be = flow.evalEb(i1, i2, u_cxx, v_cxx)
    avg_err = (se2 * (alpha**2) + be**2).sum()
    print "Torch H&S Error (%2d iterations) : %.3e %.3e %.3e" % (N, se2.sum()**0.5, be.sum(), avg_err**0.5)

    u_py = torch.core.array.float64_2(i1.shape()); u_py.fill(0)
    v_py = torch.core.array.float64_2(i1.shape()); v_py.fill(0)
    for i in range(N):
      u_py, v_py = HornAndSchunckFlowPython(alpha, i1, i2, None, u_py, v_py)
    se2 = flow.evalEc2(u_py, v_py)
    be = flow.evalEb(i1, i2, u_py, v_py)
    avg_err = (se2 * (alpha**2) + be**2).sum()
    print "Python H&S Error (%2d iterations) : %.3e %.3e %.3e" % (N, se2.sum()**0.5, be.sum(), avg_err**0.5)

    u_ocv1, v_ocv1 = compute_flow_opencv(alpha, N/4, if1, if2)
    u_ocv2, v_ocv2 = compute_flow_opencv(alpha, N/2, if1, if2)
    u_ocv, v_ocv = compute_flow_opencv(alpha, N, if1, if2)
    se2 = flow.evalEc2(u_ocv, v_ocv)
    be = flow.evalEb(i1, i2, u_ocv, v_ocv)
    avg_err = (se2 * (alpha**2) + be**2).sum()
    print "OpenCV H&S Error (%2d iterations): %.3e %.3e %.3e" % (N, se2.sum()**0.5, be.sum(), avg_err**0.5)

    u_c = u_cxx/u_ocv
    v_c = v_cxx/v_ocv
    self.assertTrue(u_c.mean() < 1.1) #check for within 10%
    self.assertTrue(v_c.mean() < 1.1) #check for within 10%
    print "mean(u_ratio), mean(v_ratio): %.3e %.3e" % (u_c.mean(), v_c.mean()),
    print "(as close to 1 as possible)"

if __name__ == '__main__':
  sys.argv.append('-v')
  if os.environ.has_key('TORCH_PROFILE') and \
      os.environ['TORCH_PROFILE'] and \
      hasattr(torch.core, 'ProfilerStart'):
    torch.core.ProfilerStart(os.environ['TORCH_PROFILE'])
  os.chdir(os.path.realpath(os.path.dirname(sys.argv[0])))
  unittest.main()
  if os.environ.has_key('TORCH_PROFILE') and \
      os.environ['TORCH_PROFILE'] and \
      hasattr(torch.core, 'ProfilerStop'):
    torch.core.ProfilerStop()
