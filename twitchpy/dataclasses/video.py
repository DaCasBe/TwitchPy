class Video:
    """
    Represents a video
    """

    def __init__(
        self,
        id,
        user_id,
        user_name,
        title,
        description,
        created_at,
        published_at,
        url,
        thumbnail_url,
        viewable,
        view_count,
        language,
        type,
        duration,
    ):
        """
        Args:
            id (str): ID of the video
            user_id (str): ID of the owner of the video
            user_name (str): User name of the owner of the video
            title (str): Title of the video
            description (str): Description of the video
            created_at (str): Date of creation of the video
            published_at (str): Date of publication of the video
            url (str): URL of the video
            thumbnail_url (str): URL of the preview image of the video
            viewable (str): Indicates whether the video is publicly viewable
            view_count (int): Number of times the video has been viewed
            language (str): Language of the video
            type (str): Type of the video
            duration (str): Duration of the video
        """

        self.id = id
        self.user_id = user_id
        self.user_name = user_name
        self.title = title
        self.description = description
        self.created_at = created_at
        self.published_at = published_at
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.viewable = viewable
        self.view_count = view_count
        self.language = language
        self.type = type
        self.duration = duration
