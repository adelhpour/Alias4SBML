import os
import libsbml
import tellurium as te
import SBMLDiagrams

from typing import Union


class Alias4SBML:

    def __init__(self):
        self.document = None
        self.layout = None
        self.local_render = None
        self.layout_is_added = False

    def load(self, sbml: str):
        if os.path.exists(sbml):
            self.document = libsbml.readSBMLFromFile(sbml)
        elif sbml.startswith('<?xml'):
            self.document = libsbml.readSBMLFromString(sbml)
        else:
            sbml = te.loada(sbml).getSBML()
            self.document = libsbml.readSBMLFromString(sbml)
        self.extract_layout_render()
        if self.layout is None:
            self.layout_is_added = True
            sb = SBMLDiagrams.load(sbml)
            sb.autolayout()
            self.document = libsbml.readSBMLFromString(sb.export())
            self.extract_layout_render()

        return self

    def save(self, file_name=""):
        if file_name:
            libsbml.writeSBMLToFile(self.document, file_name)
        else:
            return libsbml.writeSBMLToString(self.document)

    def draw(self, file_name: str =""):
        import sbmlnetwork

        sbmlnetwork.load(self.save()).draw(file_name)

    def extract_layout_render(self):
        if self.document is None:
            raise SystemExit('SBML document could not be loaded.')
        model = self.document.getModel()
        if model is None:
            raise SystemExit('Model does not exist.')

        # layout
        layout_plugin = model.getPlugin('layout')
        if layout_plugin is not None:
            number_of_layouts = layout_plugin.getNumLayouts()
            if number_of_layouts:
                self.layout = layout_plugin.getLayout(0)

        # render
        if self.layout is not None:
            render_plugin = self.layout.getPlugin("render")
            number_of_local_renders = render_plugin.getNumLocalRenderInformationObjects()
            if number_of_local_renders:
                self.local_render = render_plugin.getRenderInformation(0)

    def create_alias(self, species: Union[list, str] = [], max_species_connections: int = 4):
        if isinstance(species, str):
            species = [species]
        elif not isinstance(species, list):
            raise TypeError("species must be either a list or a string.")

        if max_species_connections <= 0:
            raise ValueError("max_species_connections must be greater than 0.")

        if self.layout:
            species_glyphs = self._get_species_glyphs(species)
            heavily_connected_species_glyphs = self.get_specified_heavily_connected_species_glyphs(species_glyphs,
                                                                                                   max_species_connections)
            for heavily_connected_species_glyph in heavily_connected_species_glyphs:
                self.create_alias_species_glyphs(heavily_connected_species_glyph)

    def get_specified_heavily_connected_species_glyphs(self, species_glyphs, max_species_connections):
        heavily_connected_species_glyphs = []
        for species_glyph in species_glyphs:
            connected_species_references = self.get_connected_species_references(species_glyph)
            if len(connected_species_references) > max_species_connections:
                heavily_connected_species_glyphs.append({"species_glyph": species_glyph,
                                                            "max_species_connections": max_species_connections,
                                                         "connected_species_references": connected_species_references})

        return heavily_connected_species_glyphs

    def get_connected_species_references(self, species_glyph):
        connected_species_references = []
        for reaction_glyph_index in range(self.layout.getNumReactionGlyphs()):
            reaction_glyph = self.layout.getReactionGlyph(reaction_glyph_index)
            for species_reference_glyph_index in range(reaction_glyph.getNumSpeciesReferenceGlyphs()):
                species_reference_glyph = reaction_glyph.getSpeciesReferenceGlyph(
                    species_reference_glyph_index)
                if species_reference_glyph.getSpeciesGlyphId() == species_glyph.getId():
                    connected_species_references.append(species_reference_glyph)

        return connected_species_references

    def get_species_glyph_id(self, name):
        for species_glyph_index in range(self.layout.getNumSpeciesGlyphs()):
            species_glyph = self.layout.getSpeciesGlyph(species_glyph_index)
            if species_glyph.getSpeciesId() == name or species_glyph.getId() == name:
                return species_glyph.getId()
            else:
                return self.get_species_glyph_from_species_text_glyphs(name)

    def get_species_glyph_from_species_text_glyphs(self, text):
        for text_glyph_index in range(self.layout.getNumTextGlyphs()):
            text_glyph = self.layout.getTextGlyph(text_glyph_index)
            if text_glyph.isSetText() and text_glyph.getText() == text:
                if text_glyph.isSetGraphicalObjectId():
                    return text_glyph.getGraphicalObjectId()

        return ""

    def create_alias_species_glyphs(self, species_info):
        original_species_glyph = species_info["species_glyph"]
        number_of_required_alias_species_glyphs = self.get_number_of_required_alias_species_glyphs(
            species_info["max_species_connections"], species_info["connected_species_references"])
        for index_of_alias_species_glyphs in range(1, number_of_required_alias_species_glyphs + 1):
            alias_species_glyph = self.layout.createSpeciesGlyph()
            alias_species_glyph.setId(
                species_info["species_glyph"].getId() + "_alias_" + str(index_of_alias_species_glyphs))
            self.set_alias_species_glyph_mutual_features(alias_species_glyph, original_species_glyph,
                                                         index_of_alias_species_glyphs)
            new_x = 0
            new_y = 0
            number_of_connected_species_references = len(species_info["connected_species_references"]) > (
                    number_of_required_alias_species_glyphs - index_of_alias_species_glyphs + 1) * species_info[
                                                         "max_species_connections"]
            assigned_connected_species_references = []
            while len(species_info["connected_species_references"]) > (
                    number_of_required_alias_species_glyphs - index_of_alias_species_glyphs + 1) * species_info[
                "max_species_connections"]:
                connected_species_reference = species_info["connected_species_references"].pop()
                connected_species_reference.setSpeciesGlyphId(alias_species_glyph.getId())
                connected_species_reference_point = self._species_reference_reaction_center_point(connected_species_reference)
                new_x += connected_species_reference_point[0]
                new_y += connected_species_reference_point[1]
                assigned_connected_species_references.append(connected_species_reference)
            new_x /= number_of_connected_species_references
            new_y /= number_of_connected_species_references
            x_difference = new_x - alias_species_glyph.getBoundingBox().getX()
            y_difference = new_y - alias_species_glyph.getBoundingBox().getY()
            alias_species_glyph.getBoundingBox().setX(alias_species_glyph.getBoundingBox().getX() + x_difference)
            alias_species_glyph.getBoundingBox().setY(alias_species_glyph.getBoundingBox().getY() + y_difference)

            for text_glyph_index in range(self.layout.getNumTextGlyphs()):
                alias_text_glyph = self.layout.getTextGlyph(text_glyph_index)
                if alias_text_glyph.getGraphicalObjectId() == alias_species_glyph.getId():
                    alias_text_glyph.getBoundingBox().setX(alias_species_glyph.getBoundingBox().getX())
                    alias_text_glyph.getBoundingBox().setY(alias_species_glyph.getBoundingBox().getY())

            for connected_species_reference in assigned_connected_species_references:
                self._move_connected_species_reference(connected_species_reference, x_difference, y_difference)
                reaction_glyph = self._get_reaction_glyph(connected_species_reference)
                if reaction_glyph:
                    center_x = 0
                    center_y = 0
                    for species_reference_glyph_index in range(reaction_glyph.getNumSpeciesReferenceGlyphs()):
                        species_reference_glyph = reaction_glyph.getSpeciesReferenceGlyph(species_reference_glyph_index)
                        connected_to_species_glyph_point = self._species_reference_connected_to_species_glyph_point(species_reference_glyph)
                        center_x += connected_to_species_glyph_point[0]
                        center_y += connected_to_species_glyph_point[1]
                    center_x /= reaction_glyph.getNumSpeciesReferenceGlyphs()
                    center_y /= reaction_glyph.getNumSpeciesReferenceGlyphs()
                    current_center_x, current_center_y = self._get_reaction_center(reaction_glyph)
                    x_difference = center_x - current_center_x
                    y_difference = center_y - current_center_y
                    self._set_reaction_center(reaction_glyph, x_difference, y_difference)

    @staticmethod
    def get_number_of_required_alias_species_glyphs(maximum_number_of_connected_species_reference_glyphs,
                                                    connected_species_references):
        number_of_required_alias_species_glyphs = len(connected_species_references) // maximum_number_of_connected_species_reference_glyphs
        if len(connected_species_references) % maximum_number_of_connected_species_reference_glyphs == 0:
            number_of_required_alias_species_glyphs -= 1

        return number_of_required_alias_species_glyphs

    def set_alias_species_glyph_mutual_features(self, alias_species_glyph, original_species_glyph,
                                                index_of_alias_species_glyph):
        alias_species_glyph.setSpeciesId(original_species_glyph.getSpeciesId())
        self.set_alias_graphical_object_bounding_box(alias_species_glyph, original_species_glyph.getBoundingBox())
        self.set_alias_graphical_object_style(alias_species_glyph, original_species_glyph)
        self.create_alias_species_glyph_text_glyphs(alias_species_glyph, original_species_glyph,
                                                    index_of_alias_species_glyph)

    @staticmethod
    def set_alias_graphical_object_bounding_box(alias_graphical_object, bounding_box):
        alias_graphical_object.getBoundingBox().setX(bounding_box.getX())
        alias_graphical_object.getBoundingBox().setY(bounding_box.getY())
        alias_graphical_object.getBoundingBox().setWidth(bounding_box.getWidth())
        alias_graphical_object.getBoundingBox().setHeight(bounding_box.getHeight())

    def set_alias_graphical_object_style(self, alias_graphical_object, original_graphical_object):
        if self.local_render:
            for local_style_index in range(self.local_render.getNumStyles()):
                local_style = self.local_render.getStyle(local_style_index)
                if local_style.getIdList().has_key(original_graphical_object.getId()):
                    local_style.addId(alias_graphical_object.getId())

    def create_alias_species_glyph_text_glyphs(self, alias_species_glyph, original_species_glyph,
                                               index_of_alias_species_glyph):
        for text_glyph_index in range(self.layout.getNumTextGlyphs()):
            original_text_glyph = self.layout.getTextGlyph(text_glyph_index)
            if original_text_glyph.getGraphicalObjectId() == original_species_glyph.getId():
                alias_text_glyph = self.layout.createTextGlyph()
                alias_text_glyph.setId(alias_species_glyph.getId() + "_text")
                alias_text_glyph.setGraphicalObjectId(alias_species_glyph.getId())
                alias_text_glyph.setOriginOfTextId(original_text_glyph.getOriginOfTextId())
                self.set_alias_text_glyph_mutual_features(alias_text_glyph, original_text_glyph,
                                                          index_of_alias_species_glyph)

    def set_alias_text_glyph_mutual_features(self, alias_text_glyph, original_text_glyph, index_of_alias_species_glyph):
        if original_text_glyph.isSetText():
            alias_text_glyph.setText(original_text_glyph.getText())
        self.set_alias_graphical_object_bounding_box(alias_text_glyph, original_text_glyph.getBoundingBox())
        self.set_alias_graphical_object_style(alias_text_glyph, original_text_glyph)

    def _get_species_glyphs(self, targeted_species):
        if self.layout:
            species_glyphs = []
            for species_glyph_index in range(self.layout.getNumSpeciesGlyphs()):
                species_glyph = self.layout.getSpeciesGlyph(species_glyph_index)
                if species_glyph.getSpeciesId() in targeted_species or len(targeted_species) == 0:
                    species_glyphs.append(species_glyph)

            return species_glyphs

        return []

    def _species_reference_reaction_center_point(self, connected_species_reference):
        if not self.layout_is_added:
            if connected_species_reference.getRoleString() in ["reactant", "substrate", "product", "sideproduct", "sidesubstrate", "side product", "side substrate"]:
                first_segment = connected_species_reference.getCurve().getCurveSegment(0)
                return first_segment.getStart().getXOffset(), first_segment.getStart().getYOffset()
            else:
                last_segment = connected_species_reference.getCurve().getCurveSegment(connected_species_reference.getCurve().getNumCurveSegments() - 1)
                return last_segment.getEnd().getXOffset(), last_segment.getEnd().getYOffset()
        else:
            if connected_species_reference.getRoleString() in ["product", "sideproduct", "side product"]:
                first_segment = connected_species_reference.getCurve().getCurveSegment(0)
                return first_segment.getStart().getXOffset(), first_segment.getStart().getYOffset()
            else:
                last_segment = connected_species_reference.getCurve().getCurveSegment(connected_species_reference.getCurve().getNumCurveSegments() - 1)
                return last_segment.getEnd().getXOffset(), last_segment.getEnd().getYOffset()

    def _species_reference_connected_to_species_glyph_point(self, connected_species_reference):
        if not self.layout_is_added:
            if connected_species_reference.getRoleString() in ["reactant", "substrate", "product", "sideproduct", "sidesubstrate", "side product", "side substrate"]:
                last_segment = connected_species_reference.getCurve().getCurveSegment(connected_species_reference.getCurve().getNumCurveSegments() - 1)
                return last_segment.getEnd().getXOffset(), last_segment.getEnd().getYOffset()
            else:
                first_segment = connected_species_reference.getCurve().getCurveSegment(0)
                return first_segment.getStart().getXOffset(), first_segment.getStart().getYOffset()
        else:
            if connected_species_reference.getRoleString() in ["product", "sideproduct", "side product"]:
                last_segment = connected_species_reference.getCurve().getCurveSegment(connected_species_reference.getCurve().getNumCurveSegments() - 1)
                return last_segment.getEnd().getXOffset(), last_segment.getEnd().getYOffset()
            else:
                first_segment = connected_species_reference.getCurve().getCurveSegment(0)
                return first_segment.getStart().getXOffset(), first_segment.getStart().getYOffset()

    def _move_connected_species_reference(self, connected_species_reference, x_difference, y_difference):
        if not self.layout_is_added:
            if connected_species_reference.getRoleString() in ["reactant", "substrate", "product", "sideproduct", "sidesubstrate", "side product", "side substrate"]:
                last_segment = connected_species_reference.getCurve().getCurveSegment(connected_species_reference.getCurve().getNumCurveSegments() - 1)
                last_segment.setEnd(last_segment.getEnd().getXOffset() + x_difference, last_segment.getEnd().getYOffset() + y_difference)
                if last_segment.getTypeCode() == 102:
                    last_segment.setBasePoint2(last_segment.getEnd().getXOffset(), last_segment.getEnd().getYOffset())
            else:
                first_segment = connected_species_reference.getCurve().getCurveSegment(0)
                first_segment.setStart(first_segment.getStart().getXOffset() + x_difference,
                                      first_segment.getStart().getYOffset() + y_difference)
                if first_segment.getTypeCode() == 102:
                    first_segment.setBasePoint1(first_segment.getStart().getXOffset(), first_segment.getStart().getYOffset())
        else:
            if connected_species_reference.getRoleString() in ["product", "sideproduct", "side product"]:
                last_segment = connected_species_reference.getCurve().getCurveSegment(connected_species_reference.getCurve().getNumCurveSegments() - 1)
                last_segment.setEnd(last_segment.getEnd().getXOffset() + x_difference, last_segment.getEnd().getYOffset() + y_difference)
                if last_segment.getTypeCode() == 102:
                    last_segment.setBasePoint2(last_segment.getEnd().getXOffset(), last_segment.getEnd().getYOffset())
            else:
                first_segment = connected_species_reference.getCurve().getCurveSegment(0)
                first_segment.setStart(first_segment.getStart().getXOffset() + x_difference,
                                      first_segment.getStart().getYOffset() + y_difference)
                if first_segment.getTypeCode() == 102:
                    first_segment.setBasePoint1(first_segment.getStart().getXOffset(), first_segment.getStart().getYOffset())


    def _get_reaction_glyph(self, connected_species_reference):
        for reaction_glyph_index in range(self.layout.getNumReactionGlyphs()):
            reaction_glyph = self.layout.getReactionGlyph(reaction_glyph_index)
            for species_reference_glyph_index in range(reaction_glyph.getNumSpeciesReferenceGlyphs()):
                species_reference_glyph = reaction_glyph.getSpeciesReferenceGlyph(species_reference_glyph_index)
                if self._are_the_same_species_references(species_reference_glyph, connected_species_reference):
                    return reaction_glyph

        return None

    def _are_the_same_species_references(self, species_reference_glyph1, species_reference_glyph2):
        if species_reference_glyph1.getId() == species_reference_glyph2.getId() and species_reference_glyph1.getRoleString() == species_reference_glyph2.getRoleString() \
            and species_reference_glyph1.getSpeciesGlyphId() == species_reference_glyph2.getSpeciesGlyphId():
            return True

        return False

    def _get_reaction_center(self, reaction_glyph):
        if reaction_glyph.getCurve() and reaction_glyph.getCurve().getNumCurveSegments():
            center_x = 0
            center_y = 0
            for curve_segment_index in range(reaction_glyph.getCurve().getNumCurveSegments()):
                curve_segment = reaction_glyph.getCurve().getCurveSegment(curve_segment_index)
                center_x += curve_segment.getStart().getXOffset()
                center_y += curve_segment.getStart().getYOffset()
            return center_x / reaction_glyph.getCurve().getNumCurveSegments(), center_y / reaction_glyph.getCurve().getNumCurveSegments()
        else:
            return reaction_glyph.getBoundingBox().getX() + reaction_glyph.getBoundingBox().getWidth() / 2, reaction_glyph.getBoundingBox().getY() + reaction_glyph.getBoundingBox().getHeight() / 2

    def _set_reaction_center(self, reaction_glyph, x_difference, y_difference):
        if reaction_glyph.getCurve() and reaction_glyph.getCurve().getNumCurveSegments():
            for curve_segment_index in range(reaction_glyph.getCurve().getNumCurveSegments()):
                curve_segment = reaction_glyph.getCurve().getCurveSegment(curve_segment_index)
                curve_segment.setStart(curve_segment.getStart().getXOffset() + x_difference, curve_segment.getStart().getYOffset() + y_difference)
                curve_segment.setEnd(curve_segment.getEnd().getXOffset() + x_difference, curve_segment.getEnd().getYOffset() + y_difference)
                if curve_segment.getTypeCode() == 102:
                    curve_segment.setBasePoint1(curve_segment.getStart().getXOffset(), curve_segment.getStart().getYOffset())
                    curve_segment.setBasePoint2(curve_segment.getEnd().getXOffset(), curve_segment.getEnd().getYOffset())
        else:
            reaction_glyph.getBoundingBox().setX(reaction_glyph.getBoundingBox().getX() + x_difference)
            reaction_glyph.getBoundingBox().setY(reaction_glyph.getBoundingBox().getY() + y_difference)

        for species_reference_glyph_index in range(reaction_glyph.getNumSpeciesReferenceGlyphs()):
            species_reference_glyph = reaction_glyph.getSpeciesReferenceGlyph(species_reference_glyph_index)
            if not self.layout_is_added:
                if species_reference_glyph.getRoleString() in ["reactant", "substrate", "product", "sideproduct", "sidesubstrate", "side product", "side substrate"]:
                    first_segment = species_reference_glyph.getCurve().getCurveSegment(0)
                    first_segment.setStart(first_segment.getStart().getXOffset() + x_difference, first_segment.getStart().getYOffset() + y_difference)
                    if first_segment.getTypeCode() == 102:
                        first_segment.setBasePoint1(first_segment.getStart().getXOffset(), first_segment.getStart().getYOffset())
                    if reaction_glyph.getNumSpeciesReferenceGlyphs() == 2:
                        first_segment.setBasePoint2(first_segment.getEnd().getXOffset(), first_segment.getEnd().getYOffset())
                else:
                    last_segment = species_reference_glyph.getCurve().getCurveSegment(species_reference_glyph.getCurve().getNumCurveSegments() - 1)
                    last_segment.setEnd(last_segment.getEnd().getXOffset() + x_difference, last_segment.getEnd().getYOffset() + y_difference)
                    if last_segment.getTypeCode() == 102:
                        last_segment.setBasePoint1(last_segment.getStart().getXOffset(), last_segment.getStart().getYOffset())
                    if reaction_glyph.getNumSpeciesReferenceGlyphs() == 2:
                        last_segment.setBasePoint2(last_segment.getEnd().getXOffset(), last_segment.getEnd().getYOffset())
            else:
                if species_reference_glyph.getRoleString() in ["product", "sideproduct", "side product"]:
                    first_segment = species_reference_glyph.getCurve().getCurveSegment(0)
                    first_segment.setStart(first_segment.getStart().getXOffset() + x_difference, first_segment.getStart().getYOffset() + y_difference)
                    if first_segment.getTypeCode() == 102:
                        first_segment.setBasePoint1(first_segment.getStart().getXOffset(), first_segment.getStart().getYOffset())
                    if reaction_glyph.getNumSpeciesReferenceGlyphs() == 2:
                        first_segment.setBasePoint2(first_segment.getEnd().getXOffset(), first_segment.getEnd().getYOffset())
                else:
                    last_segment = species_reference_glyph.getCurve().getCurveSegment(species_reference_glyph.getCurve().getNumCurveSegments() - 1)
                    last_segment.setEnd(last_segment.getEnd().getXOffset() + x_difference, last_segment.getEnd().getYOffset() + y_difference)
                    if last_segment.getTypeCode() == 102:
                        last_segment.setBasePoint1(last_segment.getStart().getXOffset(), last_segment.getStart().getYOffset())
                    if reaction_glyph.getNumSpeciesReferenceGlyphs() == 2:
                        last_segment.setBasePoint2(last_segment.getEnd().getXOffset(), last_segment.getEnd().getYOffset())


def load(sbml):
    instance = Alias4SBML()
    return instance.load(sbml)

