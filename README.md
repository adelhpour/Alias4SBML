# Alias4SBML

Alias4SBML is a Python package designed to improve the visualization of biological networks formatted in SBML (Systems Biology Markup Language). It addresses the challenge of cluttered network visualizations by generating alias nodes—duplicate representations of highly connected molecular components. These alias nodes redistribute interactions, reducing visual congestion and enhancing the clarity of biological models, particularly those with dense connectivity and overlapping interactions.

## Features

- **Alias Nodes for Improved Visualization:** Generate alias nodes—duplicate representations of highly connected genes, proteins, or other molecular components—to alleviate visual congestion in biological networks. This helps to distribute interactions more evenly across the network, preserving the clarity of functional relationships.
  
- **Seamless SBML Integration:** Alias4SBML integrates with SBMLDiagrams to improve the readability of SBML-formatted models. This integration is especially useful for models lacking predefined layouts, enhancing the visual clarity of complex networks without compromising structural integrity.

- **Customizable Alias Node Generation:** Provides flexibility for users to select which molecular components should be represented as alias nodes. Additionally, users can define connectivity thresholds, allowing for tailored alias node generation that fits the specific needs of their biological model.

- **Scalable and Efficient:** Alias4SBML is designed to handle both small and large-scale models. Whether you are working with a network containing dozens of species or hundreds, the package significantly improves model readability by reducing edge lengths and minimizing visual clutter.

## Installation

To install Alias4SBML, simply run the following command:

```bash
pip install alias4sbml
```


## Usage

```python
import alias4sbml

# create a model
model = '''
J0: S1 -> S2;
J1: S1 -> S3;
J2: S1 -> S4 + S5;
'''

# Load your SBML model
a4sbml = alias4sbml.load(model)

# Generate alias nodes for the model
a4sbml.create_alias(species="S1", max_species_connections=1)

# Visualize the modified model
a4sbml.draw("./test1.png")
```

## Customization

Alias4SBML provides several options for customizing the alias node generation process. Users can specify the molecular components to include in alias nodes, set connectivity thresholds for alias node creation, and adjust the appearance of alias nodes in the network visualization.

```python
import alias4sbml

# create a model
model = '''
J0: A -> B;
J1: A -> C;
J2: A -> B + C;
J3: B -> A + C;
J4: C -> A + B;
'''

# Load your SBML model
model = alias4sbml.load(model)

# Define the molecular components to include in alias nodes
components = ['A', 'B', 'C']

# Set the connectivity threshold for alias node generation
threshold = 1

#load the model
a4sbml = alias4sbml.load(model)
    
# Generate alias nodes with custom settings
model_with_alias_nodes = a4sbml.create_alias(components, threshold)

# Visualize the modified model
a4sbml.draw(model_with_alias_nodes)
```

## Contributing

If you would like to contribute to Alias4SBML, please open an issue or submit a pull request on the [GitHub repository](https://github.com/adelhpour/Alias4SBML).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/adelhpour/Alias4SBML/blob/develop/LICENSE) file for details.

## Citation

If you use Alias4SBML in your research, please cite the following paper:

Adel Heydarabadipour, Herbert M. Sauro, "Alias4SBML: A Python Package for Generating Alias Nodes in SBML Models," *arXiv:2502.11318v1*, 2025. DOI: [10.48550/arXiv.2502.11318](https://doi.org/10.48550/arXiv.2502.11318).

## Contact

For questions or support, please open an issue on the [GitHub repository](https://github.com/adelhpour/Alias4SBML).

```