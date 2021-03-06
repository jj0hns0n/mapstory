from oembed.providers import BaseProvider
from oembed.resources import OEmbedResource
from django.conf import settings
import re
from urlparse import urlparse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from geonode.maps.models import Map


class MapStoryProvider(BaseProvider):
    regex = settings.SITEURL.replace('/', '\/') + 'maps\/\d+'
    provides = True
    resource_type = 'rich'

    def request_resource(self, url, **kwargs):
        pattern = settings.SITEURL.replace('/', '\/') + 'maps\/\d+'
        result = re.match(pattern, url)
        if result is None:
            return HttpResponse(("Invalid oEmbed URL"), status=400, mimetype="text/plain")
        else:
            map_id = int(urlparse(url).path.split('/')[2])
            map_obj = get_object_or_404(Map, id=map_id)
            # we don't have a request object to use to find the current user so
            # let's just assume the user is anonymous and check the publishing status
            if map_obj.publish.status == 'Private':
                raise PermissionDenied()

        maxwidth = kwargs.get('maxwidth', None)
        maxheight = kwargs.get('maxheight', None)

        # prepare the dictionary of data to be returned as an oembed resource
        data = {
            'type': 'rich', 'provider_name': 'MapStory', 'version': '1.0',
            'width': maxwidth, 'height': maxheight, 'title': map_obj.title, 'author_name': map_obj.owner.username,
            'author_url': settings.SITEURL[:-1] + map_obj.owner.get_absolute_url() 
        }
        embed_url = settings.SITEURL[:-1] + map_obj.get_absolute_url() + '/embed'
        data['html'] = '<iframe style="border: none;" height="%s" width="%s" src="%s"></iframe>' % (maxheight, maxwidth, embed_url) 

        return OEmbedResource.create(data)
