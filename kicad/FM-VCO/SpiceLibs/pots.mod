* potentiometer models
* author Holger Vogt, Oct. 14th 2024

* Simple, no wiper limits (dangerous!)
.subckt pot1 rup w rlo params: wpos=0.3 Rtot=1k
R1 rup w {Rtot*(1-wpos)}
R2 w rlo {Rtot*wpos}
.ends

* code model 'potentiometer'
.subckt pot2 rup wp rlo params: wpos=0.35 Rtot=1k
Apot rlo wp rup potmod
.model potmod potentiometer(position={wpos} r={Rtot} log=FALSE log_multiplier=1)
.ends

* wiper limited by fcn 'limit'
.SUBCKT pot3 rup w rlo params: wpos=0.4 Rtot=1k
.param wip=limit(0.01m,{wpos},0.99999)
R1 rup w {Rtot*(1-wip)}
R2 w rlo {Rtot*(wip)}
.ENDS

* wiper position limited between 0.00001 and 0.99999
.subckt pot4 rup wiper rlo params: wpos = 0.45 Rtot = 1k
rupper rup wiper r = {(1 - ((wpos >=1) ? 0.99999 : ((wpos <= 0) ? 0.00001 : wpos))) * Rtot}
rlower wiper rlo r = {((wpos >=1) ? 0.99999 : ((wpos <= 0) ? 0.00001 : wpos)) * Rtot}
.ends

