import tellurium as te
import alias4sbml
import sbmlnetwork

model = '''
S1 -> S2 + S3;
S1 -> S4 + S5;
S1 -> S6;
S1 -> S7;
S1 -> S11;
S11 -> S12 + S13;
S11 -> S14;
S11 -> S15;
S11 -> S16 + S17;
S11 -> S21;
S21 -> S22 + S23;
S21 -> S24;
S21 -> S25;
S21 -> S26 + S27;
S21 -> S31;
S31 -> S32 + S33;
S31 -> S34;
S31 -> S35;
S31 -> S36 + S37;
S31 -> S41;
S41 -> S42 + S43;
S41 -> S44;
S41 -> S45;
S41 -> S46 + S47;
S41 -> S51;
S51 -> S52 + S53;
S51 -> S54;
S51 -> S55;
S51 -> S56 + S57;
S51 -> S61;
S61 -> S62 + S63;
S61 -> S64;
S61 -> S65;
S61 -> S66 + S67;
S61 -> S71;
S71 -> S72 + S73;
S71 -> S74;
S71 -> S75;
S71 -> S76 + S77;
S71 -> S81;
S81 -> S82 + S83;
'''

r = te.loada(model)
net = sbmlnetwork.load(r.getSBML())
net.auto_layout(max_num_connected_edges=1000)
net.set_style("power")
print(len(net.get_species_list()))
print(len(net.get_reactions_list()))
net.get_species_list().get_labels_list().set_font_size(28)
net.auto_layout(max_num_connected_edges=100)
shapes = net.get_species_list().get_shapes_list()
for shape in shapes:
    shape.set_corner_radius((0, 0))
net.settings.hide_compartment_labels()
net.get_reactions_list().get_curves_list().set_thickness(6)
net.draw("test0.pdf")
net.save("original_model.xml")
a4sbml = alias4sbml.load(net.save())
a4sbml.create_alias(max_species_connections=1)
a4sbml.save("aliased_model.xml")
sbmlnetwork.load("aliased_model.xml").draw("test.pdf")




