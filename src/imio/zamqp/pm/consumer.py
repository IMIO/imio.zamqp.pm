# encoding: utf-8

from requests.auth import HTTPBasicAuth
import cPickle
import hashlib
import requests
import time
import transaction

from ZODB.POSException import ConflictError
from zope.component.hooks import getSite
from zope.globalrequest import getRequest

from Products.CMFPlone.utils import base_hasattr
from plone import api
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from imio.zamqp.core import base

import logging
log = logging.getLogger('imio.zamqp.core')


def commit(retry_count=10):
    commited = False
    while commited is False:
        try:
            transaction.commit()
            commited = True
        except ConflictError as e:
            time.sleep(5)
            retry_count -= 1
            if retry_count <= 0:
                raise e


class Dummy(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request


class DMSMainFileConsumer(object):

    def __init__(self, folder, document_type, message):
        self.folder = self.site.unrestrictedTraverse(folder)
        self.document_type = document_type
        self.obj = base.MessageAdapter(cPickle.loads(message.body))
        self.metadata = self.obj.metadata.copy()
        self.context = Dummy(self.folder, getRequest())
        self.scan_fields = {'scan_id': '',
                            'pages_number': '',
                            'scan_date': '',
                            'scan_user': '',
                            'scanner': ''}
        self.scan_fields['version'] = self.obj.version
        keys = self.metadata.keys()
        for key in keys:
            if key in self.scan_fields:
                self.scan_fields[key] = self.metadata.pop(key)

    @property
    def site(self):
        return getSite()

    @property
    def existing_file(self):
        result = self.site.portal_catalog(
            portal_type='dmsmainfile',
            scan_id=self.scan_fields.get('scan_id'),
        )
        if result:
            return result[0].getObject()

    @property
    def file_content(self):
        url = '%s/file/%s/%s/%s' % (base.get_config('ws_url'),
                                    self.obj.client_id,
                                    self.obj.external_id,
                                    self.obj.version)
        r = requests.get(url, auth=self.http_auth)
        if r.status_code != 200:
            raise ValueError('HTTP error : %s' % r.status_code)
        if hashlib.md5(r.content).hexdigest() != self.obj.file_md5:
            raise ValueError("MD5 doesn't match")
        return r.content

    @property
    def http_auth(self):
        return HTTPBasicAuth(base.get_config('ws_login'),
                             base.get_config('ws_password'))

    def create_or_update(self):
        obj_file = NamedBlobFile(self.file_content, filename=self.obj.filename)
        the_file = self.existing_file
        if the_file:
            self.update(the_file, obj_file)
        else:
            self.create(obj_file)

    def set_scan_attr(self, main_file):
        for key, value in self.scan_fields.items():
            if value:
                setattr(main_file, key, value)
        main_file.reindexObject(idxs=('scan_id',))

    def update(self, the_file, obj_file):
        if self.obj.version < getattr(the_file, 'version', 1):
            log.info('file not updated due to an oldest version (scan_id: {0})'.format(the_file.scan_id))
            return
        api.content.delete(obj=the_file)
        document = the_file.aq_parent
        # dont modify id !
        del self.metadata['id']
        for key, value in self.metadata.items():
            if base_hasattr(document, key) and value:
                setattr(document, key, value)
        new_file = createContentInContainer(
            document,
            'dmsmainfile',
            title=self.metadata.get('file_title'),
            file=obj_file,
        )
        self.set_scan_attr(new_file)
        log.info('file has been updated (scan_id: {0})'.format(new_file.scan_id))

    def create(self, obj_file):
        raise NotImplementedError
