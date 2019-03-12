# si4all

A fake "technology" to play with. 

This is in preparation of the talk at FSiC2019 (https://wiki.f-si.org/index.php/FSiC2019).

DISLAIMER: The technology described in this project is 
entirely fake. All numbers given are just guesses. Any similarity
to a real technology is just coincidence.

Here is a rough table of contents:

* "Design manual": ```dm.pdf```
* XSection file: ```process.xs``` and ```xs.lyp``` (for display)
* Scripts:
  * DRC: ```drc/drc.lydrc```
  * Netlisting script: ```drc/netlist.lydrc```
  * Custom device (resistor) example: ```drc/custom_device.lydrc```
* Layout samples:
  * Device samples: ```devices.gds```
  * DRC test layout: ```drc_errors.gds```
  * Circuit sample:
    * ```ringo.gds``` (layout)
    * ```ringo.cir``` (netlist extracted with ```drc/netlist.lydrc```
    * ```ringo_simplified.cir``` (simplified netlist)
    * ```ringo_testbench.cir``` (testbench for ringo circuit)
    * ```models.cir``` (fake models for testbench)
  * Small circuit sample (resistor devices)
    * ```vdiv.gds``` (layout)
    * ```vdiv.cir``` (netlist extracted with ```drc/custom_device.lydrc```
    * ```vdiv_simplified.cir``` (simplified netlist)
  * Cross-section generation layout: ```xs.gds```

