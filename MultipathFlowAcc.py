#####################################
#### MULTIPATH FLOW ACCUMULATION ####
#####################################

# tools importieren

import saga_api
import numpy as np

DSM = saga_api.SG_Get_Data_Manager().Add_Grid("C:/Users/Anwender/Documents/ABStudium/Python/Kursunterlagen/9_Projekte/MulipathFlowAcc/Praxmar_DGM1m.sgrd")

#Metadaten
Cellsize = DSM.Get_Cellsize()
LLX = DSM.Get_XMin()
LLY = DSM.Get_YMin()
NX= DSM.Get_NX()
NY= DSM.Get_NY()
Nodata= DSM.Get_NoData_Value()
#print(Nodata)

print("Reading Raster...")

# Accumulation Array erstellen

DSMArray = np.empty((NY,NX))
AccumulationArray = np.empty((NY,NX))

HeightList = [] # Liste mit Höhenangabe (z-Wert) für jedes Pixel 
for gy in range(NY):
    for gx in range(NX):

        zDSM= DSM.asFloat(gx, gy)
        DSMArray[gy,gx]=zDSM
        if zDSM == Nodata:
            AccumulationArray[gy,gx]=Nodata
        else:
            AccumulationArray[gy,gx]=1.0
            HeightList.append([zDSM,(gy,gx)])

HeightList.sort(reverse=True)


#############################################################################
######## All dataset imported ###############################################
#############################################################################


for element in HeightList:
    gx, gy =element[1]
    SearchValue = DSMArray[gy,gx]
    if SearchValue ==Nodata:
        continue
        
    minHeight = 99999999999999.9
    min_gx = -1
    min_gy = -1


    ##### moving window approach


    # Moving Window definieren

    for window_gy in range(gy-1,gy+2):
        for window_gx in range(gx-1,gx+2): # definieren de Anzahl der Pixel für jedes Window

        # Differenz berechnen zwischen Search Value und NeighborValue

            if window_gx >= NX or window_gy >= NY or window_gx < 0 or window_gy < 0:
                continue
            NeighborValue = DSMArray[window_gy,window_gx]
            if NeighborValue == Nodata:
                continue
            DiffHeight = abs(SearchValue - NeighborValue)

                
            if DiffHeight < minHeight:
                minHeight = DiffHeight
                min_gx = window_gx
                min_gy = window_gy

            # Abfluss proportional verteilen

            AccumulationArray[gy,gx] += DiffHeight / DiffHeight.sum()*AccumulationArray[gy+1, gx+1]
            # Differenz / Summe aller Differenzen im Window * Ablufss
                     

        ########### end moving window #########
    
#############################################################################
######## Output #############################################################
#############################################################################

Out = saga_api.SG_Create_Grid(saga_api.SG_DATATYPE_Float,NX,NY,Cellsize,LLX,LLY,False)
Out.Assign_NoData()

print("Writing Raster...")
for gy in range(NY):
    for gx in range(NX):
        z = AccumulationArray[gy,gx]
        Out.Set_Value(gx,gy,z)

Out.Set_Name(saga_api.CSG_String("MultipathFlowAccumulation")) # Name, den man in der GUI sieht
Out.Save("C:/Users/Anwender/Documents/ABStudium/Python/Kursunterlagen/9_Projekte/MulipathFlowAcc/MultipathFlowAcc.tif")
