# Design Rule Check on GDSII File
import pya 
import xmltodict
import json 
import random

# User input : GDSII file name & available layers
gds_path = "/home/drc/si4all/drc/pymacro/data/drc_errors.gds"
drawing_layers = [  "nwell",
                    "diff",
                    "pplus", 
                    "nplus", 
                    "poly", 
                    "thickox", 
                    "polyres", 
                    "contact", 
                    "metal1", 
                    "via", 
                    "metal2", 
                    "pad", 
                    "border"]
error_layers = [    "min_contact_space", 
                    "min_contact_width", 
                    "min_contact_area", 
                    "contact_misplaced", 
                    "min_diff_area", 
                    "min_diff_cont_overlap", 
                    "min_diff_gate_overlap", 
                    "diff_nplus_crossover",
                    "min_diff_nwell_separation", 
                    "diff_nwell_crossover", 
                    "min_diff_poly_separation", 
                    "diff_pplus_crossover", 
                    "min_diff_space", 
                    "min_diff_width", 
                    "min_metal1_cont_overlap", 
                    "metal1_cont_crossover", 
                    "min_metal1_space", 
                    "min_metal1_via_overlap", 
                    "metal1_via_crossover", 
                    "min_metal1_width", 
                    "min_max_metal1_density", 
                    "min_metal2_pad_overlap", 
                    "metal2_pad_crossover", 
                    "min_metal2_space", 
                    "min_metal2_wide_narrow_separation", 
                    "min_metal2_via_overlap", 
                    "metal2_via_crossover", 
                    "min_metal2_width",
                    "min_nwell_area",
                    "min_nwell_diff_overlap",
                    "min_nwell_space",
                    "min_nwell_width",
                    "min_pad_space",
                    "min_pad_width",
                    "min_poly_contact_overlap",
                    "min_poly_contact_separation",
                    "min_poly_space",
                    "min_poly_width",
                    "min_poly_edge_length",
                    "min_poly_diff_extension",
                    "min_polyres_poly_overlap",
                    "polyres_over_diff",
                    "min_via_space",
                    "min_via_width",
                    "min_via_area", 
                    "non_manhattan",
                    "non_wellformed_gate"]
unit = "nm"

# Loading the GDS2 file for DRC
# ---------------------------------
gds_name = gds_path.split(".")
output_path = "".join([gds_name[0], "_drc.gds"])
lyp_path = "".join([gds_name[0], ".lyp"])

layout = pya.Layout()
top = layout.read(gds_path)
# ---------------------------------

# *** Drawing Layers *** 
# Extracting the layout components/shapes from each layer
# Ensure that every layer has single top cell (flattened gds required)
# ---------------------------------
lyr = {}
rgn = {}
idx = len(drawing_layers)
for i in range(0, idx):
    lyr[drawing_layers[i]] = layout.layer(i+1, 0)
    rgn[drawing_layers[i]] = pya.Region(layout.top_cell().begin_shapes_rec(lyr[drawing_layers[i]]))
# ---------------------------------

# Compute some required layer (saves duplicate computation)
# ---------------------------------
drawing_layers.append("gate")
lyr["gate"] = layout.layer(idx+1, 0)
rgn["gate"] = pya.Region(layout.top_cell().begin_shapes_rec(lyr[drawing_layers[idx]])) 
rgn["gate"] = rgn["poly"] & rgn["diff"]
idx = idx + 1

poly_edges = pya.Edges(layout.top_cell().begin_shapes_rec(lyr["poly"]))
poly_gate_edges = poly_edges.interacting(rgn["diff"])
other_poly_edges = poly_edges.not_interacting(rgn["diff"])
# ---------------------------------

# *** Error Layers ***
# Adding layers for the DRC errors to be put in
# ---------------------------------
error_idx = len(error_layers)
for i in range(0, error_idx):
    lyr[error_layers[i]] = layout.layer(i + idx + 1, 0)
# ---------------------------------

# Housekeeping
# ---------------------------------
metric = pya.Region.Metrics(0)
oppo_filter = pya.Region.OppositeFilter(0)
rect_filter = pya.Region.RectFilter(0)
# ---------------------------------

# Rules
# ---------------------------------
# Dumping output 
def dump_results(error_layer, violators):
    print("---------------------------------------------------")
    print(violators.to_s())
    print("---------------------------------------------------")
    print("---------------------------------------------------")
    layout.top_cell().shapes(lyr[error_layer]).insert(violators)
    return 0

# Rules corresponding to single layers 
# Minimum Width Check : Width of any polygon created with a specific material layer > threshold
def rule_x_W (layer, width, rule, error_layer):
    violators = rgn[layer].width_check(width, False, metric.Square, None, None, None, False, False)
    print(rule + ": " + layer + " width < " + str(width) + " " + unit)
    dump_results(error_layer, violators)
    return 0

# Minimum Space Check : Space between two polygons belonging to same layer > threshold
def rule_x_S (layer, space, rule, error_layer):
    violators = rgn[layer].space_check(space, False, metric.Square, None, None, None, False, oppo_filter.NoOppositeFilter, rect_filter.NoRectFilter, False)
    print(rule + ": " + layer + " space < " + str(space) + " " + unit)
    dump_results(error_layer, violators)
    return 0

# Minimum Area Check : Area of any polygon created with a specific layer > threshold
def rule_x_A (layer, area, rule, error_layer):
    violators = rgn[layer].with_area(0, area, False)
    print(rule + ": " + layer + " area < " + str(area) + " sq. " + unit)
    dump_results(error_layer, violators)
    return 0

# Checks corresponding to two different layers
# Minimum Overlap Check : In case two layers overlap, the edge length of the overlapping polygon > threshold 
def rule_x_y_O (layer1, layer2, dis, rule, error_layer):
    violators = rgn[layer1].enclosing_check(rgn[layer2], dis, False, metric.Square, None, None, None, True, oppo_filter.NoOppositeFilter, rect_filter.NoRectFilter, False)
    print(rule + ": " + layer1 + " overlap over " + layer2 + " < " + str(dis) + " " + unit)
    dump_results(error_layer, violators)
    return 0

# Minimum Space Check : The space between polygons created with two different (non-overlapping) layers > threshold 
def rule_x_y_S (layer1, layer2, dis, rule, error_layer):
    violators = rgn[layer1].separation_check(rgn[layer2], dis, False, metric.Square, None, None, None, False, oppo_filter.NoOppositeFilter, rect_filter.NoRectFilter, False)
    print(rule + ": " + layer1 + " to " + layer2 + " distance < " + str(dis) + " " + unit)
    dump_results(error_layer, violators)
    return 0

# Enclosing Check : Some of the layers must always be present entirely inside some other layer 
def rule_x_y_X1 (layer1, layer2, rule, error_layer):
    violators = rgn[layer2] - rgn[layer1]
    print(rule + ": no " + layer2 + " without " + layer1)
    dump_results(error_layer, violators)
    return 0

# Crossover Check : Polygons from layer X should be entirely inside or outside layer Y polygons  
def rule_x_y_X2 (layer1, layer2, rule, error_layer):
    violators = rgn[layer1].overlapping(rgn[layer2])- rgn[layer2]
    print(rule + ": " + layer1 + " must be either inside or outside " + layer2)
    dump_results(error_layer, violators)
    return 0

# Special Check for Contact : Contact should always be inside diffusion & poly layer 
def rule_cont_X (error_layer):
    violators = rgn["contact"] - (rgn["contact"].inside(rgn["diff"]) + rgn["contact"].inside(rgn["poly"]))
    print("CONT_X: contact not entirely inside diff or poly ")
    dump_results(error_layer, violators)
    return 0

# Special Check for Metal1 : Minimum and maximum density restrictions 
def rule_metal1_X(min_metal1_dens, max_metal1_dens, error_layer):
    metal1_area = rgn["metal1"].area()
    border_area = rgn["border"].area()
    
    dens = metal1_area / border_area
    if (dens <= min_metal1_dens):
        r_min_max_metal1_dens = rgn["metal1"]
        print("METAL1_X: metal1 density is less than minimum density threshold " + str(min_metal1_dens))
    elif (dens >= max_metal1_dens):
        r_min_max_metal1_dens = rgn["metal1"]
        print("METAL1_X: metal1 density is more than maximum density threshold " + str(max_metal1_dens))
    else:
        r_min_max_metal1_dens = rgn["metal1"] ^ rgn["metal1"]
        print("METAL1_X: metal1 density is neither less than minimum nor more than maximum density threshold")
    print("---------------------------------------------------")
    print("---------------------------------------------------")
    layout.top_cell().shapes(lyr[error_layer]).insert(r_min_max_metal1_dens)
    return 0

# Special Check for Metal2 : Space between narrow and wide strips in Metal2 layer restricted
def rule_metal2_X (w_threshold, space, error_layer):
    wide_metal2_edges = rgn["metal2"].width_check(w_threshold, True, metric.Projection, None,None,None, False, False).edges()
    narrow_metal2_edges = rgn["metal2"].edges() - wide_metal2_edges
    violators = wide_metal2_edges.separation_check(narrow_metal2_edges, space, False, metric.Square, None, None, None)
    print("METAL2_SW: metal2 space < " + str(space) + " " + unit + " for wide (i.e. > " + str(w_threshold) + " " + unit + ") and narrow metal lines")
    dump_results(error_layer, violators)
    return 0

# Special Check for Poly : 
def rule_poly_X1(poly_l, error_layer):
    violators = poly_edges.with_length(0, poly_l, False)
    print("POLY_X1: poly edges with length < " + str(poly_l) + " " + unit)
    dump_results(error_layer, violators)
    return 0

def rule_poly_X2(ext, error_layer):
    other_poly_edges_close_to_diff = other_poly_edges.separation_check(rgn["diff"].edges(), ext, False, metric.Projection).first_edges()
    violators = other_poly_edges_close_to_diff.interacting(poly_gate_edges)
    print("POLY_X2: poly extension over gater < " + str(ext) + " " + unit)
    dump_results(error_layer, violators)
    return 0

# Special Check for Polyres : 
def rule_polyres_X(error_layer):
    violators = rgn["diff"] & rgn["polyres"]
    print("POLYRES_X: diff not allowed under polyres")
    dump_results(error_layer, violators)
    return 0

def manhattan(error_layer):
    violators = pya.Edges()
    for l in drawing_layers: 
        non_recilinear = rgn[l].non_rectilinear()
        non_recilinear_polygon_all_edges = non_recilinear.edges()
  
        # isolate the edges which don't have 0 or 90 degree
        horizontal = non_recilinear_polygon_all_edges.with_angle(0, False)
        vertical = non_recilinear_polygon_all_edges.with_angle(90, False)
        violators1 = non_recilinear_polygon_all_edges - horizontal - vertical 
        violators = violators | violators1
    print("MANHATTAN: edges are neigther vertical nor horizontal")
    dump_results(error_layer, violators)
    return 0
  
def malformed_gate(error_layer):
    # A wellformed gate simply means not polygon corners appear inside the 
    # diff area. We also check whether the gate regions are rectangles

    print("POLY_DIFF_C: poly corners should not lie in diffusion")
    print("GATE_WELLFORMED: gate shapes not rectangular")

    # size the output shapes a little to improve visibility
    violators1 = (rgn["poly"].corners() & rgn["diff"])
    violators2 = rgn["gate"].non_rectangles()
    violators = violators1 | violators2
    dump_results(error_layer, violators)
    return 0
# ---------------------------------

# CONT_S
# ---------------------------------
min_cont_s = 360            #nm
rule_x_S("contact", min_cont_s, "CONT_S", error_layers[0])
# ---------------------------------

# CONT_W
# ---------------------------------
exact_cont_w = 180          #nm
rule_x_W("contact", exact_cont_w, "CONT_W", error_layers[1])
# ---------------------------------

# CONT_A
# ---------------------------------
exact_cont_a = exact_cont_w * exact_cont_w
rule_x_A("contact", exact_cont_a, "CONT_A", error_layers[2])
# ---------------------------------

# CONT_X
# ---------------------------------
rule_cont_X(error_layers[3])
# ---------------------------------

# DIFF_A
# ---------------------------------
min_diff_a = 500000        #nm2
rule_x_A("diff", min_diff_a, "DIFF_A", error_layers[4])
# ---------------------------------

# DIFF_CONT_O
# ---------------------------------
min_diff_cont_o = 110       #nm
rule_x_y_O ("diff", "contact", min_diff_cont_o, "DIFF_CONT_O", error_layers[5])
# ---------------------------------

# DIFF_GATE_O
# ---------------------------------
min_diff_gate_o = 420       #nm
rule_x_y_O ("diff", "gate", min_diff_gate_o, "DIFF_GATE_O", error_layers[6])
# ---------------------------------

# DIFF_NPLUS_X
# ---------------------------------
rule_x_y_X2("diff", "nplus", "DIFF_NPLUS_X", error_layers[7])
# ---------------------------------

# DIFF_NWELL_S
# ---------------------------------
min_diff_nwell_s = 300      #nm
rule_x_y_S ("diff", "nwell", min_diff_nwell_s, "DIFF_NWELL_S", error_layers[8])
# ---------------------------------

# DIFF_NWELL_X
# ---------------------------------
rule_x_y_X2("diff", "nwell", "DIFF_NWELL_X", error_layers[9])
# ---------------------------------

# DIFF_POLY_S
# ---------------------------------
min_diff_poly_s = 100       #nm
rule_x_y_S ("diff", "poly", min_diff_poly_s, "DIFF_POLY_S", error_layers[10])
# ---------------------------------

# DIFF_PPLUS_X
# ---------------------------------
rule_x_y_X2("diff", "pplus", "DIFF_PPLUS_X", error_layers[11])
# ---------------------------------

# DIFF_S
# ---------------------------------
min_diff_s = 600            #nm
rule_x_S("diff", min_diff_s, "DIFF_S", error_layers[12])
# ---------------------------------

# DIFF_W
# ---------------------------------
exact_diff_w = 500          #nm
rule_x_W("diff", exact_diff_w, "DIFF_W", error_layers[13])
# --------------------------------

# METAL1_CONT_O
# --------------------------------
min_metal1_cont_o = 60      #nm
rule_x_y_O ("metal1", "contact", min_metal1_cont_o, "METAL1_CONT_O", error_layers[14])
# ---------------------------------

# METAL1_CONT_X
# ---------------------------------
rule_x_y_X1("metal1", "contact", "METAL_CONT_X", error_layers[15])
# ---------------------------------

# METAL1_S
# ---------------------------------
min_metal1_s = 300          #nm
rule_x_S("metal1", min_metal1_s, "METAL1_S", error_layers[16])
# ---------------------------------

# METAL1_VIA_O
# ---------------------------------
min_metal1_via_o = 50       #nm
rule_x_y_O ("metal1", "via", min_metal1_via_o, "METAL1_VIA_O", error_layers[17])
# ---------------------------------

# METAL1_VIA_X
# ---------------------------------
rule_x_y_X1("metal1", "via", "METAL1_VIA_X", error_layers[18])
# ---------------------------------

# METAL1_W
# ---------------------------------
exact_metal1_w = 300       #nm
rule_x_W("metal1", exact_metal1_w, "METAL1_W", error_layers[19])
# --------------------------------

# METAL1_X
# ---------------------------------
min_metal1_dens = 0.2
max_metal1_dens = 0.8
rule_metal1_X(min_metal1_dens, max_metal1_dens, error_layers[20])
# --------------------------------

# METAL2_PAD_O
# ---------------------------------
min_metal2_pad_o = 2000     #nm
rule_x_y_O ("metal2", "pad", min_metal2_pad_o, "METAL2_PAD_O", error_layers[21])
# ---------------------------------

# METAL2_PAD_X
# ---------------------------------
rule_x_y_X1("metal2", "pad", "METAL2_PAD_X", error_layers[22])
# ---------------------------------

# METAL2_S
# ---------------------------------
min_metal2_s = 500          #nm
rule_x_S("metal2", min_metal2_s, "METAL2_S", error_layers[23])
# ---------------------------------

# METAL2_SW
# ---------------------------------
min_metal2_s = 700          #nm
min_metal2_wide_w = 3000    #nm
rule_metal2_X(min_metal2_wide_w, min_metal2_s, error_layers[24])
# ---------------------------------

# METAL2_VIA_O
# ---------------------------------
min_metal2_via_o = 100      #nm
rule_x_y_O ("metal2", "via", min_metal2_via_o, "METAL2_VIA_O", error_layers[25])
# ---------------------------------

# METAL2_VIA_X
# ---------------------------------
rule_x_y_X1("metal2", "via", "METAL2_VIA_X", error_layers[26])
# ---------------------------------

# METAL2_W
# ---------------------------------
exact_metal2_w = 400        #nm
rule_x_W("metal2", exact_metal2_w, "METAL2_W", error_layers[27])
# --------------------------------

# NWELL_A
# ---------------------------------
min_nwell_a = 2000000       #nm2
rule_x_A("nwell", min_nwell_a, "NWELL_A", error_layers[28])

# NWELL_DIFF_O
# ---------------------------------
min_nwell_diff_o = 400      #nm
rule_x_y_O ("nwell", "diff", min_nwell_diff_o, "NWELL_DIFF_O", error_layers[29])

# NWELL_S
# ---------------------------------
min_nwell_s = 1000          #nm
rule_x_S("nwell", min_nwell_s, "NWELL_S", error_layers[30])

# NWELL_W
# ---------------------------------
min_nwell_w = 1200          #nm
rule_x_W("nwell", min_nwell_w, "NWELL_W", error_layers[31])

# PAD_S
# ---------------------------------
min_pad_s = 10000           #nm
rule_x_S("pad", min_pad_s, "PAD_S", error_layers[32])

# PAD_W
# ---------------------------------
min_pad_w = 10000           #nm
rule_x_W("pad", min_pad_w, "PAD_W", error_layers[33])

# POLY_CONT_O
# ---------------------------------
min_poly_cont_o = 60        #nm
rule_x_y_O ("poly", "contact", min_poly_cont_o, "POLY_CONT_O", error_layers[34])

# POLY_CONT_S
# ---------------------------------
min_poly_cont_s = 130       #nm
rule_x_y_S ("poly", "contact", min_poly_cont_s, "POLY_CONT_S", error_layers[35])

# POLY_S
# ---------------------------------
min_poly_s = 300            #nm
rule_x_S("poly", min_poly_s, "POLY_S", error_layers[36])

# POLY_W
# ---------------------------------
min_poly_w = 250            #nm
rule_x_W("poly", min_poly_w, "POLY_W", error_layers[37])

# POLY_X1
# ---------------------------------
min_poly_edge_length = 70       #nm
rule_poly_X1(min_poly_edge_length, error_layers[38])

# ---------------------------------
# POLY_X2
min_poly_ext_over_diff = 250    #nm
rule_poly_X2(min_poly_ext_over_diff, error_layers[39])

# POLYRES_POLY_O
# ---------------------------------
min_polyres_poly_o = 300        #nm
rule_x_y_O ("polyres", "poly", min_polyres_poly_o, "POLYRES_POLY_O", error_layers[40])

# POLYRES_X
# ---------------------------------
rule_polyres_X(error_layers[41])

# VIA_S
# ---------------------------------
min_via_s = 250         #nm
rule_x_S("via", min_via_s, "VIA_S", error_layers[42])

# VIA_W
# ---------------------------------
exact_via_w = 200       #nm
rule_x_W("via", exact_via_w, "VIA_W", error_layers[43])

# VIA_A
# ---------------------------------
exact_via_a = exact_via_w * exact_via_w
rule_x_A("via", exact_via_a, "VIA_A", error_layers[44])

# MANHATTAN
# ---------------------------------
manhattan(error_layers[45])

# GATE_WELLFORMED
# ---------------------------------
malformed_gate(error_layers[46])

layout.write(output_path)

# Layer Properties file creation 
# ---------------------------------
lyp_temp_init = '''<?xml version="1.0" encoding="utf-8"?>
<layer-properties>
'''
lyp_temp = ''' <properties>
  <frame-color>#COLOR</frame-color>
  <fill-color>#COLOR</fill-color>
  <frame-brightness>0</frame-brightness>
  <fill-brightness>0</fill-brightness>
  <dither-pattern>INUM</dither-pattern>
  <line-style>INUM</line-style>
  <valid>true</valid>
  <visible>true</visible>
  <transparent>false</transparent>
  <width>2</width>
  <marked>false</marked>
  <xfill>false</xfill>
  <animation>0</animation>
  <name>NAME</name>
  <source>NUM/0@1</source>
 </properties>
'''
# ---------------------------------
all_layers = []
all_layers.extend(drawing_layers)
all_layers.extend(error_layers)
lyp_file = open(lyp_path, 'w')
lyp_file.write(lyp_temp_init)
for i in range(0, idx + error_idx):
    color = "%06x" % random.randint(0, 0xFFFFFF)
    lyp_curr = lyp_temp.replace("COLOR", color)
    lyp_curr = lyp_curr.replace("NUM", str(i+1))
    lyp_curr = lyp_curr.replace("NAME", all_layers[i])
    lyp_file.write(lyp_curr)
lyp_file.write("</layer-properties>")
lyp_file.close()
# ---------------------------------
