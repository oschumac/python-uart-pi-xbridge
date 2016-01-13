#!/usr/bin/python

import json
import sys
import time
import os
import array
import math

#****************************************************************
# Oliver Schumacher
# Formel aus ->  https://lp.uni-goettingen.de/get/text/5826 genutzt danke dafuer !!!
# Ausgefuehrt ist die Linieare gewichtete Regression 
# Es sollten mehrere Datensaetze erzeugt werden um eine vernuenftige Calibrierung zu erzeugen.
# Methoden -> 	clear()
#
#          -> 	newval(newxRaw, newyValue, newWeight)
#		newxRaw   = Rohdaten
#		newyValue = Calibrierungswert
#		newWeight = Gewicht der Calibierung kann z.B. 0-100 % sein
#		return linregression.intercept und linregression.slope
#
#	   -> 	getval()
#		return linregression.intercept und linregression.slope
#
#
#
#
 
class linregression:
        debug=1
        def __init__(self):
                self._id=0
                self.len=0	
                self.xRawSum=0.0
                self.xRawMed=0.0
                self.xRawMax=0.0
                self.xRawMin=400.0
                self.xRawRange=0.0
		
                self.yValueSum=0.0
                self.yValueMed=0.0
                self.yValueMax=0.0
                self.yValueMin=400.0
                self.yValueRange=0.0
                
                self.xRaw=0.0
                self.yValue=0.0
                self.weight=0.0

                self.sum_weight=0.0
                self.sum_WX=0.0
                self.sum_WXX=0.0
                self.sum_WXY=0.0
                self.sum_WY=0.0
                self.delta=0.0
                self.intercept=0.0
                self.slope=0.0
                self.check=0

                if self.debug :
                        print "Klasse " + " wurde erzeugt"

	#def __del__(self):
		#print "Klasse " + " zerstoert"

        def clear(self):
                self._id=0
                self.len=0	
                self.xRawSum=0.0
                self.xRawMed=0.0
                self.xRawMax=0.0
                self.xRawMin=400.0
                self.xRawRange=0.0
		
                self.yValueSum=0.0
                self.yValueMed=0.0
                self.yValueMax=0.0
                self.yValueMin=400.0
                self.yValueRange=0.0
                
                self.xRaw=0.0
                self.yValue=0.0
                self.weight=0.0

                self.sum_weight=0.0
                self.sum_WX=0.0
                self.sum_WXX=0.0
                self.sum_WXY=0.0
                self.sum_WY=0.0
                self.delta=0.0
                self.intercept=0.0
                self.slope=0.0
                self.check=0


        def calcstatistic(self):
                self.xRawSum+=self.xRaw
                self.xRawMed=self.xRawSum / self.len
                self.xRawMax = max(self.xRawMax,self.xRaw)
                self.xRawMin = min(self.xRawMin,self.xRaw)
                self.xRawRange = self.xRawMax - self.xRawMin 
		
                self.yValueSum+=self.yValue
                self.yValueMed=self.yValueSum / self.len
                self.yValueMax = max(self.yValueMax,self.yValue)
                self.yValueMin = min(self.yValueMin,self.yValue)
                self.yValueRange  = self.yValueMax - self.yValueMin

        def calc_dsi_mul2(self):
                tmpxRaw = self.xRaw * 2
                tmpyValue = self.yValue * 2

                if self.debug :
                        print "(calc_dsi_mul2) tmpxRaw      -> " + str(tmpxRaw)
                        print "(calc_dsi_mul2) tmpyValue    -> " + str(tmpyValue)
                        print "(calc_dsi_mul2) self.weight  -> " + str(self.weight)
                
                temp_sum_weight = self.sum_weight + self.weight
                temp_sum_WX     = self.sum_WX     + self.weight * tmpxRaw
                temp_sum_WXX    = self.sum_WXX    + self.weight * tmpxRaw * tmpxRaw
                temp_sum_WXY    = self.sum_WXY    + self.weight * tmpxRaw * tmpyValue
                temp_sum_WY     = self.sum_WY     + self.weight * tmpyValue
                
                self.delta     = ( temp_sum_weight * temp_sum_WXX ) - ( temp_sum_WX * temp_sum_WX  )
                self.slope     = (( temp_sum_weight * temp_sum_WXY ) - ( temp_sum_WX * temp_sum_WY  )) / self.delta
                self.intercept = (( temp_sum_WXX    * temp_sum_WY  ) - ( temp_sum_WX * temp_sum_WXY )) / self.delta

                if self.debug :
                        print "(calc_dsi_mul2) self.delta       ->" + str(self.delta)
                        print "(calc_dsi_mul2) self.slope       ->" + str(self.slope)
                        print "(calc_dsi_mul2) self.intercept       ->" + str(self.intercept)	

        def calc_dsi_median(self):
                tmpxRaw = self.xRaw * 2
                tmpyValue = self.yValue * 2
                if self.debug :
                        print "(calc_dsi_median) tmpxRaw      -> " + str(tmpxRaw)
                        print "(calc_dsi_median) tmpyValue    -> " + str(tmpyValue)
                        print "(calc_dsi_median) self.weight  -> " + str(self.weight)
                
                temp_sum_weight = self.sum_weight + self.weight
                temp_sum_WX     = self.sum_WX     + self.weight * tmpxRaw
                temp_sum_WXX    = self.sum_WXX    + self.weight * tmpxRaw * tmpxRaw
                temp_sum_WXY    = self.sum_WXY    + self.weight * tmpxRaw * tmpyValue
                temp_sum_WY     = self.sum_WY     + self.weight * tmpyValue
                
                self.delta     = ( temp_sum_weight * temp_sum_WXX ) - ( temp_sum_WX * temp_sum_WX  )
                self.slope     = (( temp_sum_weight * temp_sum_WXY ) - ( temp_sum_WX * temp_sum_WY  )) / self.delta
                self.intercept = (( temp_sum_WXX    * temp_sum_WY  ) - ( temp_sum_WX * temp_sum_WXY )) / self.delta

                if self.debug :
                        print "(calc_dsi_median) self.delta       ->" + str(self.delta)
                        print "(calc_dsi_median) self.slope       ->" + str(self.slope)
                        print "(calc_dsi_median) self.intercept       ->" + str(self.intercept)
                
        def calc_dsi_std(self):
                self.delta     = ( self.sum_weight * self.sum_WXX * 1.0) - ( self.sum_WX * self.sum_WX  * 1.0)
                self.slope     = (( self.sum_weight * self.sum_WXY * 1.0) - ( self.sum_WX * self.sum_WY  * 1.0)) / self.delta
                self.intercept = (( self.sum_WXX    * self.sum_WY  * 1.0) - ( self.sum_WX * self.sum_WXY * 1.0)) / self.delta	

                if self.debug :
                        print "(calc_dsi_std) self.delta       ->" + str(self.delta)
                        print "(calc_dsi_std) self.slope       ->" + str(self.slope)
                        print "(calc_dsi_std) self.intercept       ->" + str(self.intercept)

        def newval(self, newxRaw, newyValue, newWeight):

                self.len+=1
                self.xRaw = newxRaw
                self.yValue = newyValue
                self.weight = newWeight

                self.calcstatistic()		

                if self.debug :
                        print "newxRaw          ->" + str(newxRaw)
                        print "newyValue        ->" + str(newyValue)
                        print "newWeight        ->" + str(newWeight)
                        print "yValueRange      ->" + str(self.yValueRange)
                        print "xRawRange        ->" + str(self.xRawRange)
                
                
                self.sum_weight	+= newWeight
                self.sum_WX     += newWeight * newxRaw
                self.sum_WXX    += newWeight * newxRaw * newxRaw
                self.sum_WXY    += newWeight * newxRaw * newyValue
                self.sum_WY     += newWeight * newyValue

                if self.debug :
                        print "self.sum_weight  ->" + str(self.sum_weight)
                        print "self.sum_WX      ->" + str(self.sum_WX)
                        print "self.sum_WXX     ->" + str(self.sum_WXX)
                        print "self.sum_WXY     ->" + str(self.sum_WXY)
                        print "self.sum_WY      ->" + str(self.sum_WY)
                
                
		
                if len>1:
                        if self.xRawRange>50 and self.yValueRange > 50:
                                self.calc_dsi_std()	
                        else:
                                self.calc_dsi_mul2()
		
                else:
                        self.calc_dsi_mul2()

                print "Test -> " +str((newxRaw*self.slope)+self.intercept)
                return self.slope, self.intercept

        def getval(self):
                return self.slope, self.intercept
def main():
        x = linregression()
        print x.newval(130,120,10)
        print x.newval(100,121,10)
        print x.newval(100,121,100)
        print x.newval(100,121,100)
        print x.newval(100,121,100)
        print x.newval(100,121,100)
        print x.newval(100,121,100)
        print x.newval(100,121,100)
        print x.newval(100,121,100)
        print x.newval(100,121,100)
        
	

if __name__ == "__main__":
        main()

