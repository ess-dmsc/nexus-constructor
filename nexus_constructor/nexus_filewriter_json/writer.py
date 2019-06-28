from nexus_constructor.instrument import Instrument


def generate_json(data: Instrument):
    """
    Returns a formatted json string built from a given Instrument
    The json description can be used by the file writer (github.com/ess-dmsc/kafka-to-nexus) to create a NeXus file

    :param data: The full description of the beamline and data
    :return: A string containing a json representation of the data
    """
    raise NotImplementedError
