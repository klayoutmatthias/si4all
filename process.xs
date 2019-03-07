
# Input layers

height(4.0)
depth(2.0)

nwell     = layer("1/0")
diff      = layer("2/0")
pplus     = layer("3/0")
nplus     = layer("4/0")
poly      = layer("5/0")
thickox   = layer("6/0")
polyres   = layer("7/0")
contact   = layer("8/0")
metal1    = layer("9/0")
via       = layer("10/0")
metal2    = layer("11/0")
pad       = layer("12/0")

pbulk = bulk

nw = mask(nwell).grow(0.8, 0.2, :mode => :round, :into => pbulk)

pp = mask(pplus.not(poly).sized(-0.02)).grow(0.1, 0.03, :mode => :round, :into => [ nw, pbulk ])
np = mask(nplus.not(poly).sized(-0.02)).grow(0.1, 0.03, :mode => :round, :into => [ nw, pbulk ])

mask(diff.inverted.sized(0.05)).etch(0.3, 0.05, :mode => :round, :into => [ nw, pbulk, pp, np ])

fieldox = grow(0.3)
planarize(:downto => pp, :into => fieldox)

gateox = grow(0.01)

po = mask(poly).grow(0.2, :taper => 3.0)

etch(0.01, :into => gateox)

ox1 = grow(0.4)
planarize(:to => 0.4, :into => ox1)
mask(contact).etch(0.4, :taper => 3.0, :into => ox1)
ct = grow(0.4)
planarize(:downto => ox1, :into => ct)

ox2 = grow(0.25)
planarize(:to => 0.65, :into => ox2)
mask(metal1).etch(0.25, :taper => 3.0, :into => ox2)
m1 = grow(0.25)
planarize(:downto => ox2, :into => m1)

ox3 = grow(0.3)
planarize(:to => 0.95, :into => ox3)
mask(via).etch(0.3, :taper => 3.0, :into => ox3)
v1 = grow(0.3)
planarize(:downto => ox3, :into => v1)

ox4 = grow(0.4)
planarize(:to => 1.35, :into => ox4)
mask(metal2).etch(0.4, :taper => 3.0, :into => ox4)
m2 = grow(0.4)
planarize(:downto => ox4, :into => m2)

imid = mask(pad.inverted).grow(1.5, -0.3, :mode => :round)

output("1/0", pbulk)
output("2/0", nw)
output("3/0", pp)
output("4/0", np)
output("5/0", po)
output("6/0", ct)
output("7/0", m1)
output("8/0", v1)
output("9/0", m2)
output("10/0", MaterialData::new(gateox.data + fieldox.data, true))
output("11/0", MaterialData::new(ox1.data + ox2.data + ox3.data + ox4.data, true))
output("12/0", imid)


