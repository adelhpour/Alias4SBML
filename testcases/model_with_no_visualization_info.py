import alias4sbml

model = '''
J0: S1 -> S2;
J1: S1 -> S3;
J2: S1 -> S4 + S5;
'''
a4sbml = alias4sbml.load(model)
a4sbml.create_alias(species="S1", max_species_connections=1)
a4sbml.draw("aliased_model.png")
a4sbml.save("aliased_model.xml")
