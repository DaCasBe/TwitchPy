class Tag:
    """
    Represents a stream tag
    """
    
    def __init__(self,tag_id,is_auto,localization_names,localization_descriptions):
        """
        Args:
            tag_id (str): An ID that identifies the tag
            is_auto (bool): A Boolean value that determines whether the tag is an automatic tag
                            You cannot add or remove automatic tags
                            The value is true if the tag is an automatic tag; otherwise, false
            localization_names (dict): The localized names of the tag
            localization_descriptions (dict): The localized descriptions of the tag
        """

        self.tag_id=tag_id
        self.is_auto=is_auto
        self.localization_names=localization_names
        self.localization_descriptions=localization_descriptions