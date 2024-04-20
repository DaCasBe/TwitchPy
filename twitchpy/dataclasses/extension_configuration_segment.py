from dataclasses import dataclass


@dataclass
class ExtensionConfigurationSegment:
    """
    Represents a configuration segment of an extension

    Attributes:
        segment (str): The type of segment
            Possible values: broadcaster, developer, global
        broadcaster_id (str): The ID of the broadcaster that installed the extension
        content (str): The contents of the segment
        version (str): The version number that identifies this definition of the segment’s data
    """

    segment: str
    broadcaster_id: str
    content: str
    version: str
