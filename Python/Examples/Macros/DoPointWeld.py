# This macro allows simulating a spot weld gun
# It is possible to call GunOn(1) to simulate turning the gun on or GunOff(0) to stop simulating the gun

from robodk.robolink import *  # API to communicate with RoboDK

RDK = Robolink()

# quit if we are not simulating
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

# Create a new spray gun
tool = 0  # auto detect active tool
obj = 0  # auto detect object in active reference frame

#RDK.Spray_Add(tool, obj, "PARTICLE=CUBE(10,10,2) STEP=8x8")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8) STEP=8x8")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8,1,1,0.1) STEP=8x8 RANDX=3")
RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8)")
#RDK.Spray_Add(tool, obj, "STEP=8x8 RANDX=3", volume.tr(), geom.tr())
RDK.Spray_SetState(SPRAY_ON)

RDK.Render(True)

RDK.Spray_SetState(SPRAY_OFF)
