# -*- coding: utf-8 -*-

from imio.zamqp.pm.tests.base import BaseTestCase
from imio.zamqp.pm.tests.base import DEFAULT_SCAN_ID
from Products.PloneMeeting.utils import get_annexes


class TestOverrides(BaseTestCase):

    def test_pod_template_generation_context(self):
        """When generating a document from a POD template,
           the generation context contains 'zamqp_utils'."""
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        view = item.restrictedTraverse('@@document-generation')
        # zamqp_utils
        pod_template = self.meetingConfig.podtemplates.itemTemplate
        helper_view = view.get_generation_context_helper()
        generation_context = view.get_base_generation_context(helper_view, pod_template)
        self.assertTrue('zamqp_utils' in generation_context)
        self.assertTrue('scan_id' in generation_context)
        # in addition to values added by PloneMeeting
        self.assertTrue('tool' in generation_context)
        self.assertTrue('meetingConfig' in generation_context)

    def test_store_pod_template_as_annex_temporary_scan_id(self):
        """When a template is generated without having been stored
           scan_id is subject to change, in this case, we append a specific
           value saying Title of stored annex may be customized depending on
           pod_template.store_as_annex_title_expr."""
        pod_template, annex_type, item = self._setupStorePodAsAnnex()

        self.changeUser('pmManager')
        self.request.set('template_uid', pod_template.UID())
        self.request.set('output_format', 'odt')
        self.request.set('store_as_annex', '1')
        view = item.restrictedTraverse('@@document-generation')
        # by default, store_as_annex = '0'
        helper = view.get_generation_context_helper()
        self.request.set('store_as_annex', '0')
        self.assertEqual(helper.get_scan_id(),
                         u'{0}\n[Temporary QR code!]'.format(DEFAULT_SCAN_ID))
        self.request.set('store_as_annex', '1')
        self.assertEqual(helper.get_scan_id(), DEFAULT_SCAN_ID)

        # when stored as annex, generating the POD template will return correct QR code
        view()
        helper = view.get_generation_context_helper()
        self.request.set('store_as_annex', '0')
        self.assertEqual(helper.get_scan_id(), DEFAULT_SCAN_ID)
        self.request.set('store_as_annex', '1')
        self.assertEqual(helper.get_scan_id(), DEFAULT_SCAN_ID)

    def test_store_pod_template_as_annex_temporary_scan_id_batch_action(self):
        """Test that temporary label is not displayed when using the batch action."""
        cfg = self.meetingConfig
        pod_template, annex_type, item = self._setupStorePodAsAnnex()
        # make sure store_as_annex='0', setup in _setupStorePodAsAnnex
        self.request.set('store_as_annex', '0')

        # configure batch action
        cfg.setMeetingItemTemplatesToStoreAsAnnex(['itemTemplate__output_format__odt'])

        # create meeting with items
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        form = meeting.restrictedTraverse('@@store-items-template-as-annex-batch-action')

        # store annex for every items
        uids = [brain.UID for brain in meeting.get_items(ordered=True, the_objects=False)]
        self.request.form['form.widgets.uids'] = u','.join(uids)
        self.request.form['form.widgets.pod_template'] = u'itemTemplate__output_format__odt'
        form.update()
        form.handleApply(form, None)
        items = meeting.get_items(ordered=True)
        i = 1
        for an_item in items:
            annexes = get_annexes(an_item)
            self.assertEqual(len(annexes), 1)
            self.assertEqual(annexes[0].scan_id, u'01399990000000' + str(i))
            i += 1
