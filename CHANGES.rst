Changelog
=========

0.17 (2023-09-04)
-----------------

- Moved `collective.iconifiedcategory` `ContentCategory` overrides
  back to `Products.PloneMeeting`.
  [gbastien]
- Cleaned code:

  - removed event that deleted copied annexes with a `scan_id`,
    now managed by `Products.PloneMeeting`;
  - removed setup for `scan_id` index, done by `collective.dms.scanbehavior`.

  [gbastien]
- Take into account new parameter `MeetingConfig.annexEditorMayInsertBarcode`
  in `InsertBarcodeView.may_insert_barcode`.
  [gbastien]

0.16 (2023-02-27)
-----------------

- Adapted call to `imio.zamqp.core.utils.next_scan_id` where typo in parameter
  `cliend_id_var` was fixed to `client_id_var`.
  [gbastien]

0.15 (2022-06-14)
-----------------

- In `consumer._manage_after_scan_change_annex_type_to`, set the `content_category`
  on the adapted context (with `IIconifiedCategorization` behavior) so the
  `@content_category.setter` is called and default values are adapted accordingly.
  [gbastien]

0.14 (2022-01-07)
-----------------

- Fixed call to `ToolPloneMeeting.isManager`, when called with
  `realManagers=True`, no context can be passed.
  [gbastien]

0.13 (2022-01-03)
-----------------

- Use `notifyModifiedAndReindex(idxs=['scan_id'])` that will only update relevant
  modification data and `scan_id` after barcode inserted in PDF file.
  [gbastien]

0.12 (2021-11-26)
-----------------

- Use unrestricted catalog query in `AfterScanChangeAnnexTypeToVocabulary`.
  [gbastien]
- Optimize ram.cache for `ToolPloneMeeting.isManager` by calling it with cfg as context.
  [gbastien]

0.11 (2021-11-08)
-----------------

- Fixed `test_store_pod_template_as_annex_temporary_scan_id_batch_action` as
  `MeetingConfig.meetingItemTemplateToStoreAsAnnex` (single value) was renamed to
  `MeetingConfig.meetingItemTemplatesToStoreAsAnnex` (multi valued).
  [gbastien]
- Fixed `test_may_insert_barcode`, now that we use roles
  `Editor/Reader/Contributor` in `MeetingItem` workflow.
  [gbastien]
- Fixed `test_store_pod_template_as_annex_temporary_scan_id_batch_action` broken
  because Meeting moved from AT to DX.
  [gbastien]
- Do not use devpi.imio.be index anymore for buildout.
  [gbastien]
- Factorized use of `DEFAULT_SCAN_ID` in tests.
  [gbastien]

0.10 (2020-05-28)
-----------------

- Moved all the GS types profile logic to `Products.PloneMeeting`,
  by default it will behave like if `imio.zamqp.pm` was enabled.
  [gbastien]

0.9 (2020-04-29)
----------------

- Added test for `MeetingStoreItemsPodTemplateAsAnnexBatchActionForm` to ensure
  that `Temporary QR code` label is not used in stored annex.
  [gbastien]
- Add a `portal_message` when an annex is removed during duplication
  because it holds a `scan_id`.
  [gbastien]

0.8 (2020-03-12)
----------------

- When cloning an item, make sure annexes having a `scan_id` are not kept.
  [gbastien]
- Added test for `get_scan_id` that appends a value `Temporary` if generated
  when pod template still not stored as annex.
  [gbastien]
- Fixed tests after changes in `collective.iconifiedcategory`, do not create an
  annex at the portal root, it is an impossible usecase but create annex in an
  item stored in a PloneMeeting folder.
  [gbastien]

0.7 (2019-05-16)
----------------

- Makes IZPMAnnexPrettyLinkAdapter inherits from PMAnnexPrettyLinkAdapter as it
  is now overrided in Products.PloneMeeting.
  [gbastien]
- Rely on parameter `ToolPloneMeeting.enabledScanDocs` to know if action
  `insert-barcode` is available and to add additional context to the document
  generation helper view.
  [gbastien]
- Make `scan_id` computation work when template is used in a loop template.
  [gbastien]

0.6 (2018-12-04)
----------------

- Fixed tests by using PMLayer as base testing layer and defining correct
  OO_PORT and PYTHON_UNO env variables.
  [gbastien]

0.5 (2018-01-31)
----------------

- Added possibility to save a version of the annex when inserting the barcode
  if parameter `version_when_barcode_inserted` is set to `True` and when the
  scanned file is reinjected if parameter `version_when_scanned_file_reinjected`
  is set to `True` likewise.
  [gbastien]
- Define relevant behaviors for portal_type `annexDecision` using `purge=True`.
  [gbastien]
- Fixed code as `imio.zamqp.core.consumer.file_portal_type` was renamed to
  `imio.zamqp.core.consumer.file_portal_types`, it returns a list of
  portal_types to query to get the existing file, the first of these
  portal_types is used by `imio.zamqp.core.consumer.creation_file_portal_type`
  to determinate portal_type to create.
  [gbastien]
- When updating file, update scan attributes as well : `scan_date`, `scan_user`,
  `page_numbers`, `scanner`, ...
  [gbastien]

0.4 (2017-12-21)
----------------

- Use the `consume` method from `imio.zamqp.core` to consume the message to
  avoid duplicating code.
  [gbastien]
- Import `PdfReadError` from `PyPDF2`, `imio.helpers` uses it instead
  deprecated `pyPdf`.
  [gbastien]

0.3 (2017-12-06)
----------------

- In field `after_scan_change_annex_type_to`, added possibility to select an
  item_decision_annex on an item_annex and the other way round. This way the
  annex can be turned from an item annex to an item decision annex
  after scan process.
  [gbastien]
- Changed default values for `X` and `Y` coordinates used by the
  `@@insert-barcode` view so it is inserted in the top right corner by default.
  [gbastien]

0.2 (2017-11-28)
----------------

- Added `scan_id` to `AMQPPMDocumentGenerationView.get_base_generation_context`.
  [gbastien]

0.1 (2017-11-27)
----------------

- Initial release.
  [gbastien]
- Added `@@insert-barcode` view.
  [gbastien]
- Make tests rely on PloneMeetingTestCase.
  [gbastien]
- Added possibility to change the `content_category` of an annex when it's
  file is updated and make it configurable on the `ContentCategory` object thru
  the `after_scan_change_annex_type_to` field.
  [gbastien]
- Use helper `imio.zamqp.pm.utils.next_scan_id_pm` that calls
  `imio.zamqp.core.utils.next_scan_id` to be sure that relevant parameters are
  always passed correctly.
  [gbastien]
