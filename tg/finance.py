"""
Quantitative Analysis for Finance.
"""

#from numpy import recfromcsv,arange,zeros,ones,sqrt,sum,abs
import numpy as np
from matplotlib import pyplot, ticker # should use pylab rather than pyplot so that functions can be used instead of objects
import scipy.io.matlab as mat
from datetime import date
import scipy.optimize as opt 
import scipy.signal as sig
import time


#__all__ = ['plot','format_date','sticks_demo','build_predictor','sticks_demo','wdrange','build_predictor']

def plot(x=[],y=[],s='b.',title='Data Plot',xlabel='Time',label='',xtn='.PNG'):
  """
  Simplified version of matplotlib.plot

  x = horizontal axis coordinates in a numpy array
  y = vertical axis coordinates in a numpy array
  s = formatting string for matplotlib.plot (Matlab style)
  title = Plot title
  xlabel = horizontal axis label
  ylabel = vertical axis label

  returns the axis and figure objects to allow additional formating of the plot

  Notes:
    - x and y arrays must be the same length
    - multiple data sets not supported
  """
  fig=pyplot.figure()
  pyplot.clf()
  ax=pyplot.subplot(111)  
  pyplot.plot(x,y,s)
  pyplot.grid(b=True, color='gray', alpha=.8)
  fn='Fig'+str(fig.number)+'--'+title+xtn
  print 'Saving figure to file named',fn
  pyplot.savefig(fn)
  #pyplot.show()
  return (ax,fig)
 
def format_date(x, pos=None):
  """Callback for matplot.plot to format date ordinals
  """
  i=min(max(int(x+0.5),1),2000000)
  print "x =", x,"  i =", i
  return date.fromordinal(i).isoformat()

def wdrange(N,end_date=date.today()):
  """Inefficient generation of weekday ordinal array for use in date.fromordinal()
  """
  x = end_date.toordinal()+np.arange(0,-N,-1)
  while not date.fromordinal(x[0]).weekday()<5 and x[0]>0:
    print date.fromordinal(x[0])
    print date.fromordinal(x[0]).weekday()
    x[0]=x[0]-1;
  for i in range(len(x)-1):
    x[i+1]=x[i]-1
    while not date.fromordinal(x[i+1]).weekday()<5 and x[i+1]>0:
      x[i+1] = x[i+1]-1
  #x.sort()
  x=x[-1::-1]
  return x
  
def sticks(date_ordinal=[],close=[],high=[],low=[],title='Security Price Time Series'):
  """
  Crude duplicate of similar functions in matplotlib.finance
  """
  if len(high) <> len(close):
    high = close*1.1
  if len(low) <> len(close):
    low = close*0.9
  print date_ordinal,close,high,low,title
  if len(date_ordinal)<>len(close):
    x=wdrange(len(close))
  # Plot of financial data with vertical lines for high/low and horizontal tick for close
  (ax,fig)=plot(date_ordinal,close, '_')
  ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
  fig.autofmt_xdate()
  for label in ax.xaxis.get_ticklabels():
    label.set_color('blue')
    label.set_rotation(-90)
    label.set_fontsize(10)
  ax.vlines(date_ordinal, ymin=low, ymax=high)
  ax.grid(b=True, color='gray', alpha=.8)
  return ax,fig
  
def sticks_demo(N=25):
  """
  Basic demonstration of sticks plot function
      
  Warning: This demo must be run twice before vertical bars
  will be displayed due to a matplotlib bug.
  """
  
  x = np.arange(N)
  y = x**1.4
  x = wdrange(N)
  ax,fig=sticks(date_ordinal=x,close=y,high=1.1*y,low=.9*y,title='Security Price "Sticks" Plot Demo')
  #pyplot.show()
  return ax, fig

def prediction_error(alpha,x,y):
  return np.sqrt(np.sum((y-np.sum(alpha*x,axis=1))**2,axis=None)/len(y))

global optimizer_cycle_count
optimizer_cycle_count = 0
def optimizer_status(xk):
  global optimizer_cycle_count
  optimizer_cycle_count=optimizer_cycle_count+1
  if not optimizer_cycle_count%1000:
    print "      cycles = ",optimizer_cycle_count
    print "     mean(x) = ",sum(xk)/len(xk)
    print "mean(abs(x)) = ",sum(abs(xk))/len(xk)
    print "      std(x) = ",np.sqrt(sum(xk**2)/len(xk))
#    print " predict err = ",prediction_error(xk,x,y)
    print "-----------------------------------------------"

def datenum2ordinal(dn=719529):
  """ 
  Convert and Excel/Windows/Microsoft daynum to a Python date ordinal 
  """
  #dt = date(1970,1,1)-date(1,1,1);
  # In datenum convention, Jan 1, 1970 is 719529.
  datenum_for_posix_epoch=719529;
  # In python, datetime(1970,1,1).toordinal() gives 719163
  ordinal_for_posix_epoch=719163;
  ordinal_to_datenum_offset=datenum_for_posix_epoch-ordinal_for_posix_epoch
  ordinal_days=np.array(dn)-ordinal_to_datenum_offset
  return ordinal_days

def build_predictor(Nwin=5,Nres=128,Dwin=1,tol=1e-4,maxiter=1e4,symbol='GE',xtn='.PNG'):
  """
  Nwin    = number of trading days in the window of data used in the filter
  Nres    = number of days to reserve at end of data set to check performance
  Dwin    = number of trading days between samples used within the filter
  tol     = optimizer tolerance for cost function (largest cost function imrovement that can be ignored)
  symbol  = ticker symbol to load price history for (from local CSV files or from finance.yahoo.com)
  xtn     = file extension (file type) for plots saved as image files (.PNG,.JPG,.SVG,.EMF,etc)
  maxiter = maximum number of cycles through optimization algorithm (maximum function evaluations = maxiter*2)
  """
  r=np.recfromcsv('/home/hobs/Desktop/References/quant/lyle/data/'+symbol+'_yahoo.csv',skiprows=1)
  r.sort()
  r.high = r.high * r.adj_close / r.close # adjust the high and low prices for stock splits
  r.low = r.low * r.adj_close / r.close # adjust the high and low prices for stock splits
  daily_returns =  r.adj_close[1:]/r.adj_close[0:-1] - 1
  Isplit = Nres+Nwin
#  r_reserved = r[-Isplit:] # would be good to run the test repeatedly, optimizing for different portions of the data and backtesting for other portions
#  r = r[:-Isplit] 
#  daily_returns_reserved = daily_returns[-Isplit:] # needs a +1
#  daily_returns = daily_returns[:-Isplit] # needs a +1
  #r = r[-60:]  # get the last 60 days
  Ndat = len(daily_returns)-Isplit #Ndat-1 # after backdifferencing, the data set is one shorter
  Nfilt = int((Nwin-1)/Dwin + 1) # length of alpha, the vector of filter coefficients
  Ntests = int(Ndat-Nwin) # need an unfit daily return sample at the end in order to verify the accurace of the predicted return
  x = np.zeros((Ntests,Nfilt),dtype=float)
  window_sampler = np.arange(0,Nwin,Dwin)
  for i0 in range(Ntests):
    x[i0,:]    = daily_returns[window_sampler+i0]
  xres = np.zeros((Nres,Nfilt),dtype=float)
  for i0 in range(Nres):
    xres[i0,:] = daily_returns[window_sampler+i0+len(daily_returns)-Isplit]
  y = daily_returns[Nwin:-Isplit]
  yres = daily_returns[-Nres:]
  # it seems that the date column (r.date) is an integer datenum using the Octave datenum convention
  # python doesn't have a year 0 like Octave
  # The datenum epoch is Jan 1, 0000 or datenum=1.
  # In python: (datetime.datetime(2010,1,1)-datetime.datetime(1970,1,1)).days gives 14610 days
  # In Octave: datenum(2010,1,1)-datenum(1970,1,1) also gives 14610
  date_ordinal = datenum2ordinal(r.date);

  t0=time.clock()
  # retall = boolean to indicate returning parameters at each iteration
  # ftol = function tolerance
  # xtol = input paramter tolerance
  # maxiter = maximum number of optimizer iterations
  # maxfun = maximum number of cost function evaluations
  alpha = opt.fmin(prediction_error, np.ones(Nfilt)/Nfilt, args=(x,y), xtol=tol*2, ftol=tol, maxiter=maxiter, maxfun=maxiter*2, callback=optimizer_status) 
  dt=time.clock()-t0

  print '------------------------------------------------------'
  print 'Answer after',dt/60,'minutes of optimization '
  print '------------------------------------------------------'
  print "Filter coefficients (alpha) =",alpha

  res_predictions = np.sum(alpha*xres,axis=1)
  res_prediction_errors = yres-res_predictions
  res_prediction_sign_errors = np.abs(np.sign(yres)-np.sign(res_predictions))>0
  res_signed_prediction_error_ave = np.sum(res_prediction_errors)/len(res_prediction_errors)
  res_prediction_error_magnitude = np.sum(np.abs(res_prediction_errors))/len(res_prediction_errors) 
  res_prediction_error_std = np.sqrt(np.sum(np.abs(res_prediction_errors)**2)/len(res_prediction_errors))
  res_prediction_std = np.sqrt(np.sum(res_predictions**2)/len(res_predictions))
  res_average_daily_return_magnitude = np.sum(np.abs(yres))/len(yres)

  print '------------------------------------------------------'
  print 'Results when predictor applied to reserved data:'
  print '------------------------------------------------------'
  print 'average prediction error =',100.0*res_signed_prediction_error_ave/res_average_daily_return_magnitude,"%"
  print 'percent of predictions in wrong direction =',100.0*np.sum(res_prediction_sign_errors)/len(res_predictions),"%"
  print 'number of days with big predictions =',np.sum(np.abs(res_predictions)>res_prediction_std*1.5)
  print 'percent of big predictions in wrong direction =',100.0*np.sum((np.abs(res_predictions)>res_prediction_std*1.5)*res_prediction_sign_errors)/np.sum(np.abs(res_predictions)>res_prediction_std*1.5),"%"
  print 'average daily return magnitude =',100.0*res_average_daily_return_magnitude,"%"
  print 'std dev of prediction error =',100.0*res_prediction_error_std,"%"
  print 'std dev of prediction =',100.0*res_prediction_std,"%"

  title=['Filter Coefficients','Daily Returns, Predicted and Actual','Prediction Error','Prediction Errors & Daily Returns']
  f=0
  (ax,fig)=plot(x=range(len(alpha)),y=alpha,s='o',xtn='.PNG')

  f=f+1
  fig = pyplot.figure(f+1)
  pyplot.clf()
  ax = pyplot.subplot(111)
  ax.hist(yres,bins=int(len(yres)/8),log=True,label='Daily Returns')
  ax.hist(res_prediction_errors,bins=int(len(yres)/8),log=True,alpha=.5,label='Nonincestuous Prediction Errors')
  ax.legend()
  ax.grid(b=True, color='gray', alpha=.8)
  ax.set_title(title[f])
  pyplot.savefig('Fig'+str(fig.number)+'--'+title[f]+xtn)

  pyplot.show()
  return alpha

def lfilt(f,g):
  return sig.lfilter(f,1,g)[len(f)-len(g):]  

def lfilt_demo():
  f=.1*(np.arange(4)+1)
  g=np.arange(10)+1
  fg = lfilt(f,g)
  print "f =",f
  print "g =",g
  print "g filtered by f =",fg
  print "(which should be [3,4,5,6,7,8])"

def show_predictions(alpha='alpha',symbol='GE',xtn='.PNG'):
  if type(alpha)==str:
    print('Loading file named '+alpha+'.mat')
    a=mat.loadmat(alpha+'.mat',mat_dtype=False)  # load a matlab style set of matrices from the file named by the string alpha
    if a.has_key(alpha):
      alpha=a.get(alpha).reshape(-1) # get the variable with the name of the string in alpha
    else:
      alpha=a.get(a.keys()[2]).reshape(-1) # get the first non-hidden key and reshape into a 1-D array
  print('Loading financial data for stock symbol',symbol)
  r=np.recfromcsv('/home/hobs/Desktop/References/quant/lyle/data/'+symbol+'_yahoo.csv',skiprows=1)
  r.sort()
  r.high = r.high * r.adj_close / r.close # adjust the high and low prices for stock splits
  r.low = r.low * r.adj_close / r.close # adjust the high and low prices for stock splits
  daily_returns =  r.adj_close[1:]/r.adj_close[0:-1] - 1
  predictions = lfilt(alpha,daily_returns)
  print('Plotting a scatter plot of',len(daily_returns),'returns vs',len(predictions),'predictions using a filter of length',len(alpha))
  (ax,fig)=plot(predictions,daily_returns[len(alpha):],s='bo',xtn='.PNG')
  ax.set_xlabel('Predicted Returns')
  ax.set_ylabel('Actual Returns')
  big_mask = np.abs(predictions)>np.std(predictions)*1.2
  bigs = predictions[big_mask]
  true_bigs = daily_returns[big_mask]
  (ax,fig)=plot(bigs,true_bigs,s='r.',xtn='.PNG')
  fig.show()
  return (predictions,daily_returns,bigs,true_bigs,big_mask)

  
  

