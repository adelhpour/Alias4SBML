import tellurium as te
import alias4sbml
import sbmlnetwork

model = '''
S1 -> S2 + S3;
S1 -> S4 + S5;
S1 -> S6;
S1 -> S7;
'''

r = te.loada(model)
net = sbmlnetwork.load(r.getSBML())
net.auto_layout(max_num_connected_edges=100)
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
net.draw("test1.pdf")
a4sbml = alias4sbml.load(net.save())
a4sbml.create_alias(max_species_connections=1)
a4sbml.save("aliased_model.xml")
sbmlnetwork.load("aliased_model.xml").draw("test2.pdf")