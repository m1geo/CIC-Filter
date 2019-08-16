#!/usr/bin/python3

# A simple script to help me understand CIC filters.
# The decimation rate and stages are selectable.
#
# George Smart, M1GEO. 16 August 2019.
# Downloaded from https://github.com/m1geo/CIC-Filter

class integrator:
	def __init__(self):
		self.yn  = 0
		self.ynm = 0
	
	def update(self, inp):
		self.ynm = self.yn
		self.yn  = (self.ynm + inp)
		return (self.yn)
		
class comb:
	def __init__(self):
		self.xn  = 0
		self.xnm = 0
	
	def update(self, inp):
		self.xnm = self.xn
		self.xn  = inp
		return (self.xn - self.xnm)

## If this code is run (as opposted to called as a class)
if __name__ == "__main__":
	import time
	import random
	import math
	import matplotlib.pyplot as plt
	import numpy as np
	np.random.seed(0xBABECAFE)
	
	print("\n\nSimple CIC decimating filter demonstation")
	print(" Written in Python3. George Smart, M1GEO ")
	print("george-smart.co.uk       github.com/m1geo\n\n")

	## Configuration
	samples            = 64000+1	# extra one to ensure the combs run on the final iteration.
	decimation         = 64 		# any integer; powers of 2 work best.
	stages             = 5			# pipelined I and C stages

	## Function to generate an input sample
	def inp_samp(x):
		z = 0
		z += 10 * random.randint(-10000,10000)/10000 # noise
		z += 10 * np.sin(2 * np.pi * 40 * x)
		z += 10 * np.sin(2 * np.pi * 400 * x)
		z += 10 * np.sin(2 * np.pi * 4000 * x)
		z += 10 * np.sin(2 * np.pi * 40000 * x)
		return z
	
	## Calculate normalising gain
	gain = (decimation * 1) ** stages

	## Seperate Stages - these should be the same unless you specifically want otherwise.
	c_stages = stages
	i_stages = stages

	## Generate Input/Output Vectors
	print("Generating input vector... ", end="")
	input_samples    = [inp_samp(a/samples) for a in range(samples)]
	output_samples   = []
	print("Done")

	## Generate Integrator and Comb lists (Python list of objects)
	intes = [integrator() for a in range(i_stages)]
	combs = [comb()	      for a in range(c_stages)]

	## Decimating CIC Filter
	print("Running filter, this may take a while... ", end="")
	for (s, v) in enumerate(input_samples):
		z = v
		for i in range(i_stages):
			z = intes[i].update(z)
		
		if (s % decimation) == 0: # decimate is done here
			for c in range(c_stages):
				z = combs[c].update(z)
				j = z
			output_samples.append(j/gain) # normalise the gain

	print("Done")

	## Crude function to FFT and slice data, with 20log10 result
	def fft_this(data):
		N = len(data)
		return (20*np.log10(np.abs(np.fft.fft(data)) / N)[:N // 2])

	## Plot some graphs
	print("Preparing graphs... ", end="")
	plt.figure(1)
	plt.suptitle("Simple Test of Decimating CIC filter")

	plt.subplot(2,2,1)
	plt.title("Time domain input")
	plt.plot(input_samples)
	plt.grid()

	plt.subplot(2,2,3)
	plt.title("Frequency domain input")
	plt.plot(fft_this(input_samples))
	plt.grid()

	plt.subplot(2,2,2)
	plt.title("Time domain output")
	plt.plot(output_samples)
	plt.grid()

	plt.subplot(2,2,4)
	plt.title("Frequency domain output")
	plt.plot(fft_this(output_samples))
	plt.grid()
	print("Done")

	## Try to calculate the frequency rolloff. Just for indication!
	## These much match signals in the "inp_samp()" function.
	print("")
	fos = fft_this(output_samples)
	try:
		f = 40
		f2 = f * 10
		print("Filtered Output, bin %4d = %f" % (f,  fos[f]))
		print("Filtered Output, bin %4d = %f" % (f2, fos[f2]))
		print("Difference %f in a decade" % (fos[40] - fos[400]))
	except:
		print("*** Error: Cannot FFT bins must be chosen to match decimation and frequencies in the inp_samp() function.")
		pass

	## Show graphs
	plt.show()
