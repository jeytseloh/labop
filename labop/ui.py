import uml
from labop import Primitive, Protocol, SampleArray, SampleData, SampleMap, SampleMask


def protocol_template():
    """
    Create a template instantiation of a protocol.  Used for populating UI elements.
    :param
    :return: str
    """
    return f'protocol = labop.Protocol(\n\t"Identity",\n\tname="Name",\n\tdescription="Description")'


Protocol.template = protocol_template


def primitive_template(self):
    """
    Create a template instantiation of a primitive for writing a protocol.  Used for populating UI elements.
    :param self:
    :return: str
    """
    args = ",\n\t".join(
        [
            f"{parameter.property_value.template()}"
            for parameter in self.parameters
            if parameter.property_value.direction == uml.PARAMETER_IN
        ]
    )
    return f"step = protocol.primitive_step(\n\t'{self.display_id}',\n\t{args}\n\t)"


Primitive.template = primitive_template


def sample_array_str(self):
    """
    Create a human readable string for a SampleArray.
    :param self:
    :return: str
    """
    return f"SampleArray(name={self.name}, container_type={self.container_type}, initial_contents={self.initial_contents})"


SampleArray.__str__ = sample_array_str


def sample_mask_str(self):
    """
    Create a human readable string for a SampleMask.
    :param self:
    :return: str
    """
    return f"SampleMask(name={self.name}, source={self.source}, mask={self.mask})"


SampleMask.__str__ = sample_mask_str


def sample_data_str(self):
    """
    Create a human readable string for a SampleData.
    :param self:
    :return: str
    """
    return f"SampleData(name={self.name}, from_samples={self.from_samples}, values={self.values})"


SampleData.__str__ = sample_data_str


def sample_map_plot(self):
    """
    Render the sample map using a matplotlib plot
    """
    self.plot()


SampleMap.plot = sample_map_plot


def sample_array_plot(self):
    """
    Render the sample array using a matplotlib plot
    """
    self.plot()


SampleArray.plot = sample_array_plot
