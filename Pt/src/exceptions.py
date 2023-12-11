'`Módulo gerador de exceções.'
from urllib.error import HTTPError

class InvalidURL(Exception): pass

class LiveStreamError(Exception): pass

class VideoUnavailable(Exception): pass

class PlaylistUnavailable(Exception): pass

class NoResolutionDesired(Exception): pass

class InternetError(Exception): pass