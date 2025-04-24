globals[time dt]
turtles-own[x gap speed acc pen last-x-plot]

to move
  ask turtles [
    set gap [x] of turtle ((who + 1) mod 22) - x - 5 + floor(who / 21) * world-width
    let relative-speed [speed] of turtle ((who + 1) mod 22) - speed
    if model = "SOVM"[
      set acc (V gap - speed) / .5]
    if model = "SOVM unstable"[
      set acc (V gap - speed) / 1]
    if model = "SFVDM"[
      set acc (V gap - speed) / 2.5 + relative-speed / 2]
    if model = "SFVDM unstable"[
      set acc (V gap - speed) / 2.5 + relative-speed / 2.7]
    if model = "Tomer et al."[
      set acc 7 * (1 - (speed * 2 + 5) / (gap + 5)) - (Z (-1 * relative-speed))^ 2 / 2 / gap - 2 * Z (speed - 20)]
    if model = "Tomer et al. unstable"[
      set acc 3 * (1 - (speed * 2 + 5) / (gap + 5)) - (Z (-1 * relative-speed))^ 2 / 2 / gap - 2 * Z (speed - 20)]
    if model = "SIDM"[
      let ss 2 + speed - speed * relative-speed / 4
      set acc 2 * (1 - (ss / gap)^ 2 - (speed / 20)^ 4)]
    if model = "SIDM unstable"[
      let ss 2 + 1 * speed - speed * relative-speed / 5
      set acc 2 * (1 - (ss / gap)^ 2 - (speed / 20)^ 4)]
    if model = "SATG"[
      let bounded-time-gap logsumexp (logsumexp (gap / logsumexp speed 1e-10 0.01) 4 -0.01) 0.1 0.01
      set acc (0.2 * (gap - speed) + relative-speed) / bounded-time-gap]
  ]
  ask turtles [
    if abs acc < 1e5 [
      set speed speed + dt * acc + sqrt(dt) * sigma / (1 + exp min(list 700 (-1e3 * (speed - 0.1)))) * random-normal 0 1
      set x x + speed * dt
    ]
  ]
end

to-report V [s]
  report 13.7 * tanh(s / 20 - .5) + 6.3
end

to-report tanh [y]
  report (1 - exp(-2 * y))/(1 + exp(-2 * y))
end

to-report Z [y]
  report (y + abs(y))/ 2
end

to-report logsumexp [a b eps]
  ifelse abs(b / eps) < 700 and abs(a / eps) < 700 [
    report eps * ln(exp(a / eps) + exp(b / eps))][
    ifelse eps > 0 [
      report max(list a b)][
      report min(list a b)
    ]
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
27
17
869
66
-1
-1
3.61
1
10
1
1
1
0
1
1
1
-115
115
-5
5
0
0
1
ticks
30

PLOT
108
92
549
539
Trajectories
Space [m]
Time [s]
0
0
0
0
true
false
"" "if precision (time mod 250) 3 = 0 [clear-all-plots ask turtles[set pen 0]]\nif time mod 1 = 0 [\n  set-plot-y-range precision ((precision (time / 250 - .5) 0) * 250) 1 precision ((precision (time / 250 - .5) 0 + 1) * 250) 1\n  set-plot-x-range -117 117\n  ask turtles [\n    ifelse pen = 0 or (abs (last-x-plot - xcor) > 20)[\n    create-temporary-plot-pen (word (max [pen] of turtles + 1))\n    set pen max [pen] of turtles + 1][\n    set-current-plot-pen (word pen)]\n    set-plot-pen-color 5;min(list max (list 0 (speed / 2)) 8)\n    if who = 21 [set-plot-pen-color blue]\n    plotxy xcor time\n    set last-x-plot xcor]]"
PENS


BUTTON
566
92
692
125
Setup
random-seed seed\nclear-all\nset dt 0.05\ncreate-turtles 22 [\n  set heading 90 set color white if who = 21 [set color blue] set size 4.5\n  set x (who - 11) * world-width / 22 set xcor x\n  set speed 5]\nreset-ticks\n
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
698
92
787
191
Move
set time precision (time + dt) 3\ntick\nmove\nask turtles[fd(speed * dt)]\n
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

SLIDER
566
199
787
232
sigma
sigma
0
1
0.6
.05
1
NIL
HORIZONTAL

PLOT
566
292
787
483
Time sequences
NIL
NIL
0
0
0
5
true
true
"" "set-plot-x-range precision ((precision (time / 250 - .5) 0) * 250) 1 precision ((precision (time / 250 - .5) 0 + 1) * 250) 1\nset-current-plot-pen \"Mean speed [m/s]\"\nplotxy time mean [speed] of turtles\nset-current-plot-pen \"Gap SD [m]\"\nplotxy time sqrt variance[gap] of turtles"
PENS
"Mean speed [m/s]" 1 0 -13345367 true "" ""
"Gap SD [m]" 1 0 -955883 true "" ""

CHOOSER
566
239
787
284
Model
model
"SOVM" "SFVDM" "Tomer et al." "SIDM" "SATG" "SOVM unstable" "SFVDM unstable" "Tomer et al. unstable" "SIDM unstable"
4

INPUTBOX
632
131
692
191
seed
22
1
0
Number

BUTTON
566
131
626
191
Random
set seed random 100
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1
@#$#@#$#@
## WHAT IS IT?

This is a tentative of reproduction of the [experiment by Sugiyama et al. (2007) [1]](https://iopscience.iop.org/article/10.1088/1367-2630/10/3/033001/meta) using different stochastic car-following models.
In the experiment, 22 vehicles drive around a 231 meters long single-lane roundabout, starting from uniform initial conditions. After a transition period, which can last several minutes, we observe the formation of a stop-and-go wave (see [youtube.com/watch?v=7wm-pZp\_mi0](https://www.youtube.com/watch?v=7wm-pZp_mi0)).
The complete trajectories of the experiment are available in [[2], Figure 2 (I)](https://iopscience.iop.org/article/10.1088/1367-2630/11/8/083025/meta)

The motion models used are stochastic extensions of the well-known car-following models:
 
* [Optimal Velocity model (1995) [3]](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.51.1035)
* [Full Velocity Difference model (2001) [4]](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.64.017101)
* [Inertial model by Tomer et al. (2000) [5]](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.84.382)
* [Intelligent Driver model (2000) [6]](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.62.1805)
* [Adaptive Time Gap model (2010) [7]](https://www.sciencedirect.com/science/article/pii/S0191261509001623).



## HOW IT WORKS

Let `x_n` and `v_n = dx_n/dt` be the position and speed of the vehicle `n` and `Dx_n = x_{n+1} - x_n - 5` the distance gap to the preding vehicle `n+1`, where `5` is the length of the vehicles, and `Dv_n = v_{n+1} - v_n` the relative speed (by taking into account the periodic boundaries). 
  
In the simulation module, the equations of motion of the vehicles are the stochastic car-following models given below.

* **Stochastic Optimal Velocity Model** (`Model: SOVM`):

>	d v_n = dt tau(V(Dx_n) - v_n) + s(v_n) dW_n.

The sensitivity parameter `tau` is set to 2 for the stable version of the model (`Model: SOVM`) and to 1 for the unstable version of the model (`Model: SOVM unstable`).

* **Stochastic Full Velocity Difference Model** (`Model: SFVDM`):

>	d v_n = dt (V(Dx_n) - v_n) / 2.5 + dt Dv_n / kappa + s(v_n) dW_n.


The sensitivity parameter `kappa` is set to 2 for the stable version of the model (`Model: SFVDM`) and to 2.7 for the unstable version of the model (`Model: SFVDM unstable`).

In the SOV and SFVD models, the optimal velocity function is given by

>	V(s)=13.7 tanh(s / 20 - .5) + 6.3.


* **Model by Tomer et al.** (`Model: Tomer et al.`)

>	d v_n = dt [K(1 - (2v_n + 5) / (Dx_n + 5)) - Z²(-Dv_n) / 2Dx_n - 2Z(v_n - 20)] + s(v_n) dW_n,

where `Z(x) = (x+|x|)/2` is the positive part of `x`. 
The sensitivity parameter `K` is set to 7 for the stable version of the model (`Model: Tomer et al.`) and to 3 for the unstable version of the model (`Model: Tomer et al. unstable`).


* **Stochastic Intelligent Driver Model** (`Model: SIDM`)

>	d v_n = dt 2(1 - (f(v_n,Dv_n) / Dx_n) ^ 2 - (v_n / 20) ^ 4) + s(v_n) dW_n

where

>	f(v_n,Dv_n)  = 2 + v_n - v_n * Dv_n / A.

The acceleration parameter `A` in `f` is set to 4 for the stable version of the model (`Model: SIDM`) and to 5 for the unstable version of the model (`Model: SIDM unstable`).

* **Stochastic Adaptive Time Gap Model** (`Model: SATG`)

>	d v_n = dt (0.2(Dx_n - v_n) + Dv_n) / T_n + s(v_n) dW_n,

where `T_n` is the molifier time gap bounded between 0.1 and 4 

>	T_n = F_eps(0.1, F_-eps(4, Dx_n / F_eps(0, v_n))),

with `F` the [SumLogExp](https://en.wikipedia.org/wiki/LogSumExp) smooth maximum (resp. minimum)

>	F_eps(a, b) = eps log( exp(a / eps) + exp(b / eps)),

where `eps=0.01`.
 
In the models, `W_n` are independent standard Wiener processes and

>	s(v) = sigma / (1 + exp(-1000(v - 0.1)))

is the noise volatility. 

The simulations are performed using an [Euler-Maruyama discretisation scheme](https://en.wikipedia.org/wiki/Euler%E2%80%93Maruyama_method). The simulation time step is deliberately large (`dt = 0.05 s`) to make the online simulation fast.


## HOW TO USE IT

Initialise and start the simulation using the `Setup` and `Move` buttons. 
Select the model using the `Model` slider.
The value of the noise volatility and the choice of the model can be changed dynamically during the simulation.
The random seed can be changed at each initialisation using the 'Seed' box or the 'Random' button.


## REFERENCES

[1]  Y. Sugiyama et al. [_New J Phys_ **10(3)**:033001 (2008)](https://iopscience.iop.org/article/10.1088/1367-2630/10/3/033001/meta)

[2]  A. Nakayama et al. [_New J Phys_ **11(8)**:083025 (2009)](https://iopscience.iop.org/article/10.1088/1367-2630/11/8/083025/meta)

[3]  M. Bando et al. [_Phys Rev E_ **51(2)**:1035 (1995)](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.51.1035).

[4]  R. Jiang et al. [_Phys Rev E_ **64(1)**:017101 (2001)](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.64.017101)

[5]  E. Tomer et al. [_Phys Rev Lett_ **84(2)**:382 (2000)](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.84.382)

[6]  M. Treiber et al. [_Phys Rev E_ **62(2)**:1805 (2000)](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.62.1805)

[7]  A. Tordeux et al. [_Transp Res B: Meth_ **44(8-9)**:1115 (2010)](https://www.sciencedirect.com/science/article/pii/S0191261509001623) 


## CREDITS

This simulation platform was created as part of the French-German project _Multi-agent modelling of dense crowd dynamics: Predict & Understand_ ([MADRAS](https://www.madras-crowds.eu/)). The project acknowledges the support of the French National Research Agency (Agence Nationale de la Recherche, ANR), grant number ANR-20-CE92-0033, and the German Research Foundation (Deutsche Forschungsgemeinschaft, DFG), grant number 446168800.


## AUTHOR

Antoine Tordeux, University of Wuppertal ([vzu.uni-wuppertal.de](https://www.vzu.uni-wuppertal.de/en/))
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.2.2
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0
-0.2 0 0 1
0 1 1 0
0.2 0 0 1
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@

@#$#@#$#@
