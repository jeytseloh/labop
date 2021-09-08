import os
import tempfile
import unittest
import filecmp
import sbol3
import paml
import tyto


# import paml_md


class TestProtocolEndToEnd(unittest.TestCase):
    def test_create_protocol(self):
        #############################################
        # set up the document
        print('Setting up document')
        doc = sbol3.Document()
        sbol3.set_namespace('https://bbn.com/scratch/')

        #############################################
        # Import the primitive libraries
        print('Importing libraries')
        paml.import_library('liquid_handling')
        print('... Imported liquid handling')
        paml.import_library('plate_handling')
        print('... Imported plate handling')
        paml.import_library('spectrophotometry')
        print('... Imported spectrophotometry')
        paml.import_library('sample_arrays')
        print('... Imported sample arrays')

        #############################################
        # Create the protocol
        print('Creating protocol')
        protocol = paml.Protocol('iGEM_LUDOX_OD_calibration_2018')
        protocol.name = "iGEM 2018 LUDOX OD calibration protocol"
        protocol.description = '''
With this protocol you will use LUDOX CL-X (a 45% colloidal silica suspension) as a single point reference to
obtain a conversion factor to transform absorbance (OD600) data from your plate reader into a comparable
OD600 measurement as would be obtained in a spectrophotometer. This conversion is necessary because plate
reader measurements of absorbance are volume dependent; the depth of the fluid in the well defines the path
length of the light passing through the sample, which can vary slightly from well to well. In a standard
spectrophotometer, the path length is fixed and is defined by the width of the cuvette, which is constant.
Therefore this conversion calculation can transform OD600 measurements from a plate reader (i.e. absorbance
at 600 nm, the basic output of most instruments) into comparable OD600 measurements. The LUDOX solution
is only weakly scattering and so will give a low absorbance value.
        '''
        doc.add(protocol)

        # create the materials to be provisioned
        ddh2o = sbol3.Component('ddH2O', 'https://identifiers.org/pubchem.substance:24901740')
        ddh2o.name = 'Water, sterile-filtered, BioReagent, suitable for cell culture'  # TODO get via tyto
        doc.add(ddh2o)

        ludox = sbol3.Component('LUDOX', 'https://identifiers.org/pubchem.substance:24866361')
        ludox.name = 'LUDOX(R) CL-X colloidal silica, 45 wt. % suspension in H2O'
        doc.add(ludox)

        # add an optional parameter for specifying the wavelength
        wavelength_param = protocol.input_value('wavelength', sbol3.OM_MEASURE, optional=True,
                                              default_value=sbol3.Measure(600, tyto.OM.nanometer))

        # actual steps of the protocol
        # get a plate
        plate = protocol.primitive_step('EmptyContainer', specification=tyto.NCIT.get_uri_by_term('Microplate'))  # replace with container ontology

        # put ludox and water in selected wells
        c_ddh2o = protocol.primitive_step('PlateCoordinates', source=plate.output_pin('samples'), coordinates='A1:D1')
        protocol.primitive_step('Provision', resource=ludox, destination=c_ddh2o.output_pin('samples'),
                                amount=sbol3.Measure(100, tyto.OM.microliter))

        c_ludox = protocol.primitive_step('PlateCoordinates', source=plate.output_pin('samples'), coordinates='A2:D2')
        protocol.primitive_step('Provision', resource=ddh2o, destination=c_ludox.output_pin('samples'),
                                amount=sbol3.Measure(100, tyto.OM.microliter))

        # measure the absorbance
        c_measure = protocol.primitive_step('PlateCoordinates', source=plate.output_pin('samples'), coordinates='A1:D2')
        measure = protocol.primitive_step('MeasureAbsorbance', samples=c_measure.output_pin('samples'), wavelength=wavelength_param)

        output = protocol.designate_output('absorbance', sbol3.OM_MEASURE,
                                           measure.output_pin('measurements'))
        protocol.order(protocol.get_last_step(), output)

        ########################################
        # Validate and write the document
        print('Validating and writing protocol')
        v = doc.validate()
        assert len(v) == 0, "".join(f'\n {e}' for e in v)

        temp_name = os.path.join(tempfile.gettempdir(), 'igem_ludox_test.nt')
        doc.write(temp_name, sbol3.SORTED_NTRIPLES)
        print(f'Wrote file as {temp_name}')

        comparison_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testfiles', 'igem_ludox_test.nt')
        # doc.write(comparison_file, sbol3.SORTED_NTRIPLES)
        print(f'Comparing against {comparison_file}')
        assert filecmp.cmp(temp_name, comparison_file), "Files are not identical"
        print('File identical with test file')

        # render and view the dot
        dot = protocol.to_dot()
        dot.render(f'{protocol.name}.gv')
        dot.view()

    # def test_protocol_to_markdown(self):
    #     doc = sbol3.Document()
    #     doc.read('test/testfiles/igem_ludox_test.nt', 'nt')
    #     paml_md.MarkdownConverter(doc).convert('iGEM_LUDOX_OD_calibration_2018')

    # Checking if files are identical needs to wait for increased stability
    # assert filecmp.cmp('iGEM_LUDOX_OD_calibration_2018.md','test/testfiles/iGEM_LUDOX_OD_calibration_2018.md')


if __name__ == '__main__':
    unittest.main()